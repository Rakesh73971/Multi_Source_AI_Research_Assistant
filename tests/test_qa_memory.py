from unittest.mock import patch, MagicMock
from app.rag.qa_service import generate_answer
from app.models.user import User
from app.models.research_session import ResearchSession
from app.models.conversation_message import ConversationMessage, MessageRole


@patch("app.rag.qa_service.ChatGoogleGenerativeAI")
def test_generate_answer_with_history(mock_llm_class):
    mock_llm = MagicMock()
    mock_llm_class.return_value = mock_llm
    mock_llm.invoke.return_value.content = "Mocked response content"

    chunks = [
        {
            "content": "Paris is the capital of France.",
            "metadata": {
                "source_id": 1,
                "chunk_index": 0,
                "source_title": "Doc1",
            },
        }
    ]
    chat_history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]

    result = generate_answer(
        "What is the capital of France?", chunks, chat_history
    )

    assert result == "Mocked response content"
    mock_llm_class.assert_called_once()

    # Verify that prompt contains history
    args, kwargs = mock_llm.invoke.call_args
    prompt_text = args[0]
    assert "User: Hello" in prompt_text
    assert "Assistant: Hi there!" in prompt_text
    assert "What is the capital of France?" in prompt_text


def test_session_service_message_history(session):
    from app.services.session_service import ask_session_question_service

    # Create test user
    db_user = User(
        full_name="History Test User",
        email="historytest@test.com",
        password="pwd",
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    # Create research session
    db_session = ResearchSession(
        user_id=db_user.id,
        name="History Session",
        chroma_collection_db="hist_col",
        status="active",
    )
    session.add(db_session)
    session.commit()
    session.refresh(db_session)

    # Create some old conversation messages
    msg1 = ConversationMessage(
        session_id=db_session.id,
        user_id=db_user.id,
        role=MessageRole.USER,
        content="What is Python?",
    )
    msg2 = ConversationMessage(
        session_id=db_session.id,
        user_id=db_user.id,
        role=MessageRole.ASSISTANT,
        content="A programming language.",
    )
    session.add(msg1)
    session.add(msg2)
    session.commit()

    # Mock agent execution to verify history is passed to run_research_agent
    with patch(
        "app.services.session_service.run_research_agent"
    ) as mock_agent:
        mock_agent.return_value = {"chunks": [], "answer": "Python is nice."}

        ask_session_question_service(
            db=session,
            session_id=db_session.id,
            question="Tell me more.",
            top_k=2,
            current_user=db_user,
        )

        mock_agent.assert_called_once()
        called_kwargs = mock_agent.call_args[1]
        assert "chat_history" in called_kwargs
        history = called_kwargs["chat_history"]

        # Ensure the history lists messages chronologically
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "What is Python?"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "A programming language."
