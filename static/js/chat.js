document.addEventListener('DOMContentLoaded', function() {
    // State variables
    let currentDocumentId = null;
    let currentDocumentName = null;
    let isUploading = false;
    let documents = [];
    
    // DOM elements
    const documentUpload = document.getElementById('document-upload');
    const documentList = document.getElementById('document-list');
    const emptyDocuments = document.getElementById('empty-documents');
    const documentTitle = document.getElementById('current-document-title');
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const uploadProgress = document.getElementById('upload-progress');
    const progressBar = uploadProgress.querySelector('.progress-bar');
    const themeSwitcher = document.getElementById('themeSwitcher');
    const backToDocumentsBtn = document.getElementById('backToDocuments');
    
    // Initialize
    loadDocuments();
    setupEventListeners();
    
    // Theme handling
    function setupEventListeners() {
        // Theme toggle
        themeSwitcher.addEventListener('click', toggleTheme);
        
        // Document upload
        documentUpload.addEventListener('change', handleDocumentUpload);
        
        // Chat form submission
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sendMessage();
        });
        
        // Back to documents (mobile view)
        if (backToDocumentsBtn) {
            backToDocumentsBtn.addEventListener('click', function() {
                const documentPanel = document.querySelector('.document-panel');
                if (documentPanel) {
                    documentPanel.style.display = 'flex';
                }
            });
        }
        
        // Auto-resize textarea
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
            if (this.scrollHeight > 150) {
                this.style.overflowY = 'auto';
            } else {
                this.style.overflowY = 'hidden';
            }
        });
    }
    
    function toggleTheme() {
        const body = document.body;
        const currentTheme = body.getAttribute('data-theme') || 'classic';
        
        // Cycle through themes: classic > amber > blue > classic
        let newTheme;
        if (currentTheme === 'classic') {
            newTheme = 'amber';
        } else if (currentTheme === 'amber') {
            newTheme = 'blue';
        } else {
            newTheme = 'classic';
        }
        
        body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Send theme preference to server
        fetch('/set_theme', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                theme: newTheme
            })
        });
    }
    
    // Document management functions
    async function loadDocuments() {
        try {
            const response = await fetch('/api/documents');
            
            if (!response.ok) {
                throw new Error('Failed to load documents');
            }
            
            const data = await response.json();
            documents = data.documents || [];
            
            renderDocumentList();
        } catch (error) {
            console.error('Error loading documents:', error);
            showErrorToast('Could not load documents. Please try again later.');
        }
    }
    
    function renderDocumentList() {
        documentList.innerHTML = '';
        
        if (documents.length === 0) {
            emptyDocuments.style.display = 'flex';
            return;
        } else {
            emptyDocuments.style.display = 'none';
        }
        
        documents.forEach(doc => {
            const docElement = document.createElement('div');
            docElement.classList.add('document-item');
            if (currentDocumentId === doc.id) {
                docElement.classList.add('active');
            }
            
            const fileIcon = getFileIcon(doc.name);
            
            docElement.innerHTML = `
                <div class="document-item-content">
                    <i class="${fileIcon}"></i>
                    <span class="document-name">${doc.name}</span>
                </div>
                <div class="document-actions">
                    <button class="delete-document" data-id="${doc.id}" title="Delete document">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            
            docElement.addEventListener('click', function(e) {
                if (!e.target.closest('.document-actions')) {
                    selectDocument(doc.id, doc.name);
                }
            });
            
            const deleteBtn = docElement.querySelector('.delete-document');
            deleteBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                deleteDocument(doc.id);
            });
            
            documentList.appendChild(docElement);
        });
    }
    
    function getFileIcon(filename) {
        const extension = filename.split('.').pop().toLowerCase();
        
        switch (extension) {
            case 'pdf':
                return 'fas fa-file-pdf';
            case 'doc':
            case 'docx':
                return 'fas fa-file-word';
            case 'txt':
                return 'fas fa-file-alt';
            default:
                return 'fas fa-file';
        }
    }
    
    async function handleDocumentUpload(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        const formData = new FormData();
        formData.append('file', file);
        
        // Check if user is logged in
        const userProfile = document.querySelector('.user-profile');
        const isLoggedIn = userProfile !== null;
        
        if (!isLoggedIn) {
            showErrorToast('Please log in to upload documents.');
            return;
        }
        
        // Check file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            showErrorToast('File size exceeds 10MB limit.');
            return;
        }
        
        // Check file type
        const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
        if (!validTypes.includes(file.type)) {
            showErrorToast('Invalid file type. Please upload PDF, DOC, DOCX, or TXT files.');
            return;
        }
        
        isUploading = true;
        uploadProgress.style.display = 'block';
        progressBar.style.width = '0%';
        
        try {
            const response = await fetch('/api/documents/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Upload failed');
            }
            
            const data = await response.json();
            
            // Reset input
            documentUpload.value = '';
            
            // Add new document to list and select it
            documents.push(data.document);
            renderDocumentList();
            selectDocument(data.document.id, data.document.name);
            
            showSuccessToast('Document uploaded successfully!');
        } catch (error) {
            console.error('Error uploading document:', error);
            showErrorToast('Failed to upload document. Please try again.');
        } finally {
            isUploading = false;
            uploadProgress.style.display = 'none';
        }
    }
    
    async function deleteDocument(docId) {
        if (!confirm('Are you sure you want to delete this document?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/documents/${docId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error('Failed to delete document');
            }
            
            // Remove from document list
            documents = documents.filter(doc => doc.id !== docId);
            
            // If current document is deleted, reset chat
            if (currentDocumentId === docId) {
                resetChat();
            }
            
            renderDocumentList();
            showSuccessToast('Document deleted successfully.');
        } catch (error) {
            console.error('Error deleting document:', error);
            showErrorToast('Failed to delete document. Please try again.');
        }
    }
    
    function selectDocument(docId, docName) {
        currentDocumentId = docId;
        currentDocumentName = docName;
        
        // Update document list
        document.querySelectorAll('.document-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const selectedDoc = [...document.querySelectorAll('.document-item')].find(item => 
            item.querySelector('.delete-document').getAttribute('data-id') === docId
        );
        
        if (selectedDoc) {
            selectedDoc.classList.add('active');
        }
        
        // Update chat UI
        documentTitle.textContent = docName;
        document.getElementById('no-document-message').style.display = 'none';
        
        // Enable message input and buttons
        messageInput.disabled = false;
        chatForm.querySelector('button').disabled = false;
        document.getElementById('clear-chat').disabled = false;
        document.getElementById('export-chat').disabled = false;
        
        // Load chat history
        loadChatHistory(docId);
        
        // On mobile, hide document panel after selection
        if (window.innerWidth <= 768) {
            const documentPanel = document.querySelector('.document-panel');
            if (documentPanel) {
                documentPanel.style.display = 'none';
            }
        }
    }
    
    async function loadChatHistory(docId) {
        try {
            chatMessages.innerHTML = '';
            addSystemMessage('Loading chat history...');
            
            const response = await fetch(`/api/chat/${docId}/history`);
            
            if (!response.ok) {
                throw new Error('Failed to load chat history');
            }
            
            const data = await response.json();
            
            // Clear messages
            chatMessages.innerHTML = '';
            
            if (data.history && data.history.length > 0) {
                data.history.forEach(msg => {
                    if (msg.role === 'user') {
                        addUserMessage(msg.content);
                    } else if (msg.role === 'assistant') {
                        addBotMessage(msg.content);
                    } else if (msg.role === 'system') {
                        addSystemMessage(msg.content);
                    }
                });
            } else {
                addSystemMessage(`Start chatting with "${currentDocumentName}"`);
            }
            
            // Scroll to bottom
            scrollToBottom();
            
        } catch (error) {
            console.error('Error loading chat history:', error);
            chatMessages.innerHTML = '';
            addSystemMessage('Failed to load chat history. Please try again.');
        }
    }
    
    function resetChat() {
        currentDocumentId = null;
        currentDocumentName = null;
        
        // Update UI
        documentTitle.textContent = 'Select a document to start chatting';
        document.getElementById('no-document-message').style.display = 'flex';
        chatMessages.innerHTML = '';
        
        // Disable message input and buttons
        messageInput.disabled = true;
        chatForm.querySelector('button').disabled = true;
        document.getElementById('clear-chat').disabled = true;
        document.getElementById('export-chat').disabled = true;
        
        // Update document list
        document.querySelectorAll('.document-item').forEach(item => {
            item.classList.remove('active');
        });
    }
    
    function addSystemMessage(text) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'system');
        messageElement.innerHTML = text;
        chatMessages.appendChild(messageElement);
        scrollToBottom();
    }
    
    function addUserMessage(text) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'user');
        messageElement.innerHTML = text;
        chatMessages.appendChild(messageElement);
        scrollToBottom();
    }
    
    function addBotMessage(text, withThinking = false) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'assistant');
        
        if (withThinking) {
            messageElement.innerHTML = `
                <div class="thinking-indicator">
                    <span>.</span><span>.</span><span>.</span>
                </div>
            `;
        } else {
            messageElement.innerHTML = formatResponse(text);
        }
        
        chatMessages.appendChild(messageElement);
        scrollToBottom();
        
        return messageElement;
    }
    
    function formatResponse(text) {
        // Convert markdown to HTML
        return marked.parse(text || "");
    }
    
    function updateBotMessage(messageElement, text) {
        messageElement.innerHTML = formatResponse(text);
        scrollToBottom();
    }
    
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    async function sendMessage() {
        const messageText = messageInput.value.trim();
        if (!messageText || !currentDocumentId) return;
        
        // Add user message
        addUserMessage(messageText);
        
        // Clear input
        messageInput.value = '';
        messageInput.style.height = 'auto';
        
        // Add thinking indicator
        const botMessageElement = addBotMessage('', true);
        
        try {
            const response = await fetch(`/api/chat/${currentDocumentId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: messageText
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to get response');
            }
            
            const data = await response.json();
            
            // Update bot message
            updateBotMessage(botMessageElement, data.response);
            
        } catch (error) {
            console.error('Error sending message:', error);
            updateBotMessage(botMessageElement, "I'm sorry, I encountered an error while processing your message. Please try again.");
        }
    }
    
    // Toast notifications
    function showSuccessToast(message) {
        showToast(message, 'success');
    }
    
    function showErrorToast(message) {
        showToast(message, 'error');
    }
    
    function showToast(message, type) {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = createToastContainer();
        }
        
        // Create toast element
        const toast = document.createElement('div');
        toast.classList.add('toast');
        toast.classList.add(type);
        
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                ${message}
            </div>
            <button class="toast-close">×</button>
        `;
        
        // Add to container
        toastContainer.appendChild(toast);
        
        // Add close event
        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.remove();
        });
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }
    
    function createToastContainer() {
        const container = document.createElement('div');
        container.classList.add('toast-container');
        document.body.appendChild(container);
        return container;
    }
}); 