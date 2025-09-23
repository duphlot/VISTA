import './App.css'
import { Chat } from './pages/chat/chat'
import { AppLayout } from './components/layout/app-layout'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext'
import { ChatProvider } from './context/ChatContext'

function App() {
  return (
    <ThemeProvider>
      <ChatProvider>
        <Router>
          <div className="w-full h-screen text-gray-900 dark:text-white">
            <Routes>
              <Route path="/" element={
                <AppLayout>
                  <Chat />
                </AppLayout>
              } />
            </Routes>
          </div>
        </Router>
      </ChatProvider>
    </ThemeProvider>
  )
}

export default App;