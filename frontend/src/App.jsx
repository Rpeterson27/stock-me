import { useState } from 'react'
import { MantineProvider } from '@mantine/core';
import { StockAnalysis } from './components/StockAnalysis';
import '@mantine/core/styles.css';
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <MantineProvider>
      <h1>StockMe</h1>
      <StockAnalysis />
    </MantineProvider>
  )
}

export default App
