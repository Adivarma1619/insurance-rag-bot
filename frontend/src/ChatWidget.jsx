import React, { useState, useEffect, useRef } from 'react'
import './ChatWidget.css'

function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [msgs, setMsgs] = useState([
    { role: 'bot', text: 'Hi! Ask me anything about your policy or claims.' }
  ])
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [msgs])

  const send = async () => {
    if (!text.trim()) return

    const userMessage = text.trim()
    setText('')

    // Add user message to chat
    setMsgs(prev => [...prev, { role: 'user', text: userMessage }])
    setLoading(true)

    try {
      // Call backend API
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: userMessage })
      })

      if (!response.ok) {
        throw new Error('Failed to get response from server')
      }

      const data = await response.json()

      // Add bot response to chat
      setMsgs(prev => [...prev, { role: 'bot', text: data.answer }])
    } catch (error) {
      console.error('Error:', error)
      setMsgs(prev => [...prev, {
        role: 'bot',
        text: 'Sorry, I encountered an error. Please try again or contact our support team.'
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <>
      {/* Floating Action Button */}
      <button
        className="chat-fab"
        onClick={() => setOpen(!open)}
        aria-label="Toggle chat"
      >
        {open ? '✕' : '💬'}
      </button>

      {/* Chat Modal */}
      {open && (
        <div className="chat-modal">
          {/* Header */}
          <div className="chat-header">
            Insurance Help
          </div>

          {/* Messages Area */}
          <div className="chat-body">
            {msgs.map((msg, i) => (
              <div
                key={i}
                className={`bubble ${msg.role}`}
              >
                {msg.text}
              </div>
            ))}
            {loading && (
              <div className="bubble bot">
                Thinking...
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="chat-input">
            <input
              type="text"
              placeholder="Type your question..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
            />
            <button
              onClick={send}
              disabled={loading || !text.trim()}
            >
              Send
            </button>
          </div>
        </div>
      )}
    </>
  )
}

export default ChatWidget
