import React from 'react'
import ChatWidget from './ChatWidget'

function App() {
  return (
    <div style={{
      fontFamily: 'Arial, sans-serif',
      padding: '40px',
      maxWidth: '800px',
      margin: '0 auto'
    }}>
      <h1 style={{
        color: '#1a1a1a',
        marginBottom: '20px'
      }}>
        Insurance Agency Website (Demo)
      </h1>
      <p style={{
        color: '#666',
        fontSize: '16px',
        lineHeight: '1.6'
      }}>
        Click <strong>Chat</strong> on the bottom-right to get instant answers about your insurance policies, claims, coverage, and more.
      </p>
      <p style={{
        color: '#666',
        fontSize: '16px',
        lineHeight: '1.6',
        marginTop: '20px'
      }}>
        Our AI-powered assistant is available 24/7 to help you with common questions. For complex issues, we'll connect you with a human agent.
      </p>

      <ChatWidget />
    </div>
  )
}

export default App
