import { useState } from 'react';
import { TextInput, Button, Paper, Text, Container, Title, LoadingOverlay } from '@mantine/core';
import axios from 'axios';

export function StockAnalysis() {
  const [ticker, setTicker] = useState('');
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generateReport = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post(`/api/report/${ticker}`);
      console.log('API Response:', response.data); // Debug log
      setReport(response.data);
      console.log('Report State:', report); // Debug log
    } catch (err) {
      console.error('Error:', err); // Debug log
      setError(err.response?.data?.detail || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container size="md" py="xl">
      <Paper p="md" radius="md" withBorder>
        <Title order={2} mb="md">What stock would you like to know about?</Title>
        
        <TextInput
          label="Stock Ticker"
          placeholder="Enter stock ticker (e.g., AAPL)"
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
          mb="md"
        />

        <Button 
          onClick={generateReport}
          disabled={!ticker || loading}
          mb="md"
        >
          Generate Report
        </Button>

        <LoadingOverlay visible={loading} />

        {error && (
          <Text color="red" mb="md">
            {error}
          </Text>
        )}

        {report && (
          <Paper p="md" radius="md" withBorder mt="md">
            <Text mb="md">Report for {ticker}:</Text>
            <pre style={{ whiteSpace: 'pre-wrap', background: '#f5f5f5', padding: '1rem', borderRadius: '4px' }}>
              {JSON.stringify(report, null, 2)}
            </pre>
          </Paper>
        )}
      </Paper>
    </Container>
  );
}