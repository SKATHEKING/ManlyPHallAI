/**
 * Frontend application for Manly P. Hall AI Bot
 * Handles user interactions and API communication
 */

const API_BASE_URL = "http://localhost:8000";
const chatArea = document.getElementById("chatArea");
const questionInput = document.getElementById("questionInput");
const askButton = document.getElementById("askButton");

/**
 * Send question to backend API and display response
 */
async function askQuestion() {
    const question = questionInput.value.trim();

    if (!question) {
        alert("Please enter a question");
        return;
    }

    // Disable input while processing
    questionInput.disabled = true;
    askButton.disabled = true;

    // Add user message to chat
    addMessage(question, "user");
    questionInput.value = "";

    // Show loading indicator
    const loadingDiv = document.createElement("div");
    loadingDiv.className = "message assistant";
    loadingDiv.innerHTML = '<div class="message-bubble loading">Thinking...</div>';
    chatArea.appendChild(loadingDiv);
    chatArea.scrollTop = chatArea.scrollHeight;

    try {
        // Make API request
        const response = await fetch(`${API_BASE_URL}/ask`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ question: question }),
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();

        // Remove loading indicator
        loadingDiv.remove();

        // Add assistant response
        addMessage(data.answer, "assistant", data.sources);
    } catch (error) {
        // Remove loading indicator
        loadingDiv.remove();

        // Show error message
        addMessage(
            `Error: ${error.message}. Make sure the backend is running at ${API_BASE_URL}`,
            "assistant"
        );
    } finally {
        // Re-enable input
        questionInput.disabled = false;
        askButton.disabled = false;
        questionInput.focus();
    }
}

/**
 * Add a message to the chat area
 * @param {string} text - Message text
 * @param {string} sender - "user" or "assistant"
 * @param {Array} sources - Optional source information
 */
function addMessage(text, sender, sources = []) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}`;

    const bubbleDiv = document.createElement("div");
    bubbleDiv.className = "message-bubble";
    bubbleDiv.textContent = text;

    messageDiv.appendChild(bubbleDiv);

    // Add sources if provided
    if (sources && sources.length > 0) {
        const sourcesDiv = document.createElement("div");
        sourcesDiv.className = "sources";
        sourcesDiv.innerHTML = "<strong>Sources:</strong><br>";

        sources.forEach((source, index) => {
            const sourceText = `${index + 1}. ${source.source_title}${
                source.chapter ? ` - ${source.chapter}` : ""
            } (score: ${source.similarity_score.toFixed(2)})`;
            sourcesDiv.innerHTML += sourceText + "<br>";
        });

        messageDiv.appendChild(sourcesDiv);
    }

    chatArea.appendChild(messageDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
}

/**
 * Check if API is available on page load
 */
window.addEventListener("load", async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log("✓ Backend is running");
        }
    } catch (error) {
        console.warn(
            `⚠ Backend not reachable at ${API_BASE_URL}. Start it with: python backend/main.py`
        );
    }
});
