from app.packages.queues.prototypes import Subscriber
from app.packages.queues.redis import RedisSubscriber
from app.packages.infrastructure.redis import redis_cli
from app.packages.constants.constants import FILES_TOPIC
from app.packages.storage import MinioClient, QdrantVectorStore
from sentence_transformers import SentenceTransformer
from io import BytesIO
import PyPDF2


class Processor:
    _subscriber: Subscriber
    _minio_client: MinioClient
    _transformer: SentenceTransformer
    _vector_store: QdrantVectorStore

    def __init__(self):
        self._subscriber = RedisSubscriber(redis_cli)
        self._minio_client = MinioClient()
        self._transformer = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self._vector_store = QdrantVectorStore()

    def run(self):
        print(f"Starting processor, subscribing to {FILES_TOPIC}...")
        for message in self._subscriber.subscribe(FILES_TOPIC):
            try:
                self._handle_file(str(message))
            except Exception as e:
                print(e)

    def terminate(self):
        self._subscriber.close()

    def _handle_file(self, file_id: str):
        print(f"Processing file: {file_id}")
        metadata = self._minio_client.stat_file(file_id)
        file = self._minio_client.download_file(file_id)
        text = ""
        match metadata.content_type:
            case "application/pdf":
                text = extract_text_from_pdf(file)
            case _:
                print(f"Unsupported file type: {metadata.content_type}")
                return

        chunks = chunk_text(text)
        print(f"Created {len(chunks)} chunks")

        if not chunks:
            print("No chunks created from text")
            return

        embeddings = self._transformer.encode(chunks, show_progress_bar=True)
        print(f"Embeddings shape: {embeddings.shape}")

        # Store embeddings and chunks in Qdrant
        result = self._vector_store.add_documents(
            file_id=file_id,
            chunks=chunks,
            embeddings=embeddings,
        )
        print(f"Stored {result['num_chunks']} chunks in Qdrant with status: {result['status']}")
        print(f"Successfully processed file: {file_id}")


def extract_text_from_pdf(content: bytes) -> str:
    try:
        pdf_stream = BytesIO(content)
        reader = PyPDF2.PdfReader(pdf_stream)

        num_pages = len(reader.pages)
        print(f"PDF has {num_pages} pages")

        text = ""
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text += page_text + "\n"
                    print(f"Page {i+1}: extracted {len(page_text)} characters")
                else:
                    print(f"Page {i+1}: no text extracted (might be scanned/image)")
            except Exception as e:
                print(f"Error extracting text from page {i+1}: {e}")
                continue

        if not text.strip():
            raise ValueError("No text could be extracted from PDF. It might be a scanned document or image-based PDF.")

        print(f"Total extracted text length: {len(text)} characters")
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        raise


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()

    if not words:
        return []

    if len(words) <= chunk_size:
        return [text]

    chunks = []
    step = max(1, chunk_size - overlap)

    for i in range(0, len(words), step):
        chunk_words = words[i:i + chunk_size]
        if chunk_words:
            chunk = ' '.join(chunk_words)
            chunks.append(chunk)

    return chunks
