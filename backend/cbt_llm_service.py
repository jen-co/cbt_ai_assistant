from langchain_community.document_loaders import TextLoader
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_experimental.text_splitter import SemanticChunker
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM, ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
import logging
import time

from .models import CogDistortionAnalysis, CogDistortionComparison
from pydantic import BaseModel
from .config import Config
from .prompts import get_cbt_rag_prompt, get_cbt_simple_prompt

logger = logging.getLogger(__name__)

class CBTLLMService:
    """
    Cognitive Behavioral Therapy LLM Service supporting both RAG and simple LLM analysis modes.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.vector_store = None
        self.retriever = None
        self.rag_chain = None  # RAG chain
        self.simple_chain = None  # Simple LLM chain
        self._ensure_rag_ready()
        self._ensure_simple_ready()
    
    def _ensure_rag_ready(self):
        """Lazily initialize RAG components if not already initialized"""
        if self.rag_chain is not None and self.retriever is not None:
            return
        try:
            self._load_documents()
            self._setup_vector_store()
            self._setup_rag_chain()
            logger.info("RAG components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG components: {str(e)}")
            raise

    def _ensure_simple_ready(self):
        """Lazily initialize simple LLM chain if not already initialized"""
        if self.simple_chain is not None:
            return
        try:
            self._setup_simple_chain()
            logger.info("Simple LLM chain initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize simple LLM chain: {str(e)}")
            raise
    
    def _load_documents(self):
        """Load and split documents"""
        try:
            loader = TextLoader(str(self.config.FULL_JOURNAL_TEXT_PATH))
            docs = loader.load()
            
            if self.config.TEXT_SPLITTER == "semantic":	
                text_splitter = SemanticChunker(HuggingFaceEmbeddings())
            elif self.config.TEXT_SPLITTER == "recursive":
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.config.CHUNK_SIZE, chunk_overlap=self.config.CHUNK_OVERLAP)
            else:
                raise ValueError(f"Invalid text splitter: {self.config.TEXT_SPLITTER}")
            
            self.documents = text_splitter.split_documents(docs)
            
            logger.info(f"Loaded {len(self.documents)} document chunks")
            
        except Exception as e:
            logger.error(f"Failed to load documents: {str(e)}")
            raise
    
    def _setup_vector_store(self):
        """Setup the vector store with embeddings"""
        try:
            embedder = HuggingFaceEmbeddings()
            self.vector_store = FAISS.from_documents(self.documents, embedder)
            self.retriever = self.vector_store.as_retriever(
                search_type="similarity", 
                search_kwargs={"k": self.config.RETRIEVER_K}
            )
            
            logger.info("Vector store setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup vector store: {str(e)}")
            raise
    
    def _setup_rag_chain(self):
        """Setup the RAG chain with prompt and LLM"""
        try:
            # Initialize LLM
            llm = ChatOllama(
                model=self.config.OLLAMA_MODEL,
                # format="json",
                # base_url=self.config.OLLAMA_BASE_URL,
                # reasoning=self.config.OLLAMA_REASONING
            )
            
            # Define the CBT prompt
            prompt = get_cbt_rag_prompt(self.config.COGNITIVE_DISTORTIONS_PATH)
            
            # Setup parser for RAG mode returning CogDistortionComparison
            parser = PydanticOutputParser(pydantic_object=CogDistortionComparison)
            
            # Create prompt template
            qa_chain_prompt = PromptTemplate.from_template(prompt).partial(format_instructions=parser.get_format_instructions())

            answer_chain = {"context": self.retriever, "question": RunnablePassthrough()} | qa_chain_prompt | llm | StrOutputParser()
            self.rag_chain = RunnableParallel(result=answer_chain, source_documents=self.retriever, query=RunnablePassthrough())
            
            logger.info("RAG chain setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup RAG chain: {str(e)}")
            raise

    def _setup_simple_chain(self):
        """Setup the simple LLM chain with prompt and LLM (no retrieval)"""
        # Initialize LLM
        llm = ChatOllama(
            model=self.config.OLLAMA_MODEL,
        )
        # Define the simple CBT prompt
        prompt = get_cbt_simple_prompt(self.config.COGNITIVE_DISTORTIONS_PATH)
        parser = PydanticOutputParser(pydantic_object=CogDistortionAnalysis)
        simple_prompt = PromptTemplate.from_template(prompt).partial(format_instructions=parser.get_format_instructions())
        # Simple chain returns a string result we will parse
        self.simple_chain = simple_prompt | llm | StrOutputParser()
    
    def _extract_json_from_markdown(self, text: str) -> str:
        """
        Extract JSON content from markdown code blocks and fix common formatting issues
        
        Args:
            text: Text that may contain JSON wrapped in markdown code blocks
            
        Returns:
            str: The extracted JSON content with formatting fixes
        """
        import re
        
        # Pattern to match JSON code blocks: ```json ... ```
        json_pattern = r'```json\s*(.*?)\s*```'
        match = re.search(json_pattern, text, re.DOTALL)
        
        if match:
            json_content = match.group(1).strip()
        else:
            # If no JSON code block found, use the original text
            json_content = text.strip()
        
        # Fix curly quotes to straight quotes
        json_content = json_content.replace('”', '"')
        json_content = json_content.replace('“', '"')
        
        return json_content
    
    def analyse_question(self, question: str, use_context: bool = False) -> tuple[BaseModel, str]:
        """
        Analyse a user's question for cognitive distortions
        
        Args:
            question: The user's question or issue to analyse
            use_context: True to use retrieval-augmented generation, False for a direct LLM chain
            
        Returns:
            tuple: (CogDistortionAnalysis, str) - The analysis results and concatenated source document content
        """
        try:
            logger.info(f"Analyzing question (use_context={use_context}): {question[:100]}...")

            start_time = time.time()

            if not use_context:
                self._ensure_simple_ready()
                raw = self.simple_chain.invoke(question)
                end_time = time.time()
                elapsed_time = end_time - start_time
                logger.info(f"Simple chain invoke took {elapsed_time:.2f} seconds")

                # Parse
                json_content = self._extract_json_from_markdown(raw)
                try:
                    analysis = CogDistortionAnalysis.model_validate_json(json_content)
                except Exception as json_error:
                    logger.error(f"JSON parsing error (simple): {str(json_error)}")
                    logger.error(f"JSON content (simple): {json_content}")
                    raise
                logger.info("Simple analysis completed successfully")
                return analysis, ""
            else:
                self._ensure_rag_ready()
                result = self.rag_chain.invoke(question)
                end_time = time.time()
                elapsed_time = end_time - start_time
                logger.info(f"RAG chain invoke took {elapsed_time:.2f} seconds")

                # Extract source documents content
                source_content = ""
                if "source_documents" in result:
                    for doc in result["source_documents"]:
                        if hasattr(doc, 'page_content'):
                            source_content += doc.page_content + "\n\n"
                        elif isinstance(doc, dict) and 'page_content' in doc:
                            source_content += doc['page_content'] + "\n\n"

                # Parse
                json_content = self._extract_json_from_markdown(result["result"])
                try:
                    analysis = CogDistortionComparison.model_validate_json(json_content)
                except Exception as json_error:
                    logger.error(f"JSON parsing error (rag): {str(json_error)}")
                    logger.error(f"JSON content (rag): {json_content}")
                    raise
                logger.info("RAG analysis completed successfully")
                return analysis, source_content
            
                # # Try to fix common JSON issues
                # fixed_result = self._fix_json_issues(result["result"])
                # try:
                #     analysis = CogDistortionAnalysis.model_validate_json(fixed_result)
                #     logger.info("Successfully fixed JSON parsing error")
                # except Exception as fixed_error:
                #     logger.error(f"Failed to fix JSON: {str(fixed_error)}")
                #     logger.error(f"Fixed result: {fixed_result}")
                #     # Create a fallback response
                #     analysis = self._create_fallback_analysis(question, result["result"])
                #     logger.info("Created fallback analysis due to JSON parsing failure")
            
            
            
        except Exception as e:
            logger.error(f"Failed to analyse question: {str(e)}")
            raise
    
    # def _fix_json_issues(self, json_str: str) -> str:
    #     """Fix common JSON formatting issues"""
    #     try:
    #         # Fix the specific issue we saw with malformed colons
    #         fixed = json_str
            
    #         # Fix malformed colons that appear without proper key-value structure
    #         import re
    #         # Find patterns like " : " without proper key structure and fix them
    #         fixed = re.sub(r'\s*:\s*"([^"]*)"\s*,\s*"([^"]*)"', r'": "\1", "\2"', fixed)
            
    #         # Fix double quotes in property names
    #         fixed = fixed.replace('" "name"', '"name"')
    #         fixed = fixed.replace('" "explanation"', '"explanation"')
    #         fixed = fixed.replace('" "questions"', '"questions"')
    #         fixed = fixed.replace('" "cognitive_disortions_issue"', '"cognitive_disortions_issue"')
    #         fixed = fixed.replace('" "cognitive_disortions_context"', '"cognitive_disortions_context"')
    #         fixed = fixed.replace('" "comparison"', '"comparison"')
            
    #         # Fix trailing commas
    #         fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
            
    #         # Fix missing quotes around property names
    #         fixed = re.sub(r'(\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*):', r'\1"\2"\3:', fixed)
            
    #         return fixed
    #     except Exception as e:
    #         logger.error(f"Error fixing JSON: {str(e)}")
    #         return json_str
    
    # def _create_fallback_analysis(self, question: str, raw_result: str) -> CogDistortionAnalysis:
    #     """Create a fallback analysis when JSON parsing fails"""
    #     from .models import CognitiveDistortion
        
    #     # Create a basic fallback response
    #     fallback_distortion = CognitiveDistortion(
    #         name="Analysis Error",
    #         explanation="The AI analysis encountered an error while processing your request. Please try rephrasing your question or try again later.",
    #         questions=[
    #             "Could you rephrase your question to be more specific?",
    #             "What specific aspect of your situation would you like to focus on?",
    #             "Are there any particular thoughts or feelings you're struggling with?"
    #         ]
    #     )
        
    #     return CogDistortionAnalysis(
    #         cognitive_disortions_issue=[fallback_distortion],
    #         cognitive_disortions_context=[fallback_distortion],
    #         comparison="Unable to complete analysis due to technical error. Please try again with a different question or rephrase your current question."
    #     )
    
    