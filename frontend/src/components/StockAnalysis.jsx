import { useState } from 'react';
import { 
  TextInput, 
  Button, 
  Paper, 
  Text, 
  Container, 
  Title, 
  LoadingOverlay,
  Stack,
  Group,
  Badge,
  Grid,
  List,
  ThemeIcon,
  Card
} from '@mantine/core';
import { IconNews, IconBrandYoutube, IconChartBar } from '@tabler/icons-react';
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
      console.log('API Response:', response.data);
      setReport(response.data);
    } catch (err) {
      console.error('Error:', err);
      setError(err.response?.data?.detail || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  // Format date string
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <Container size="lg" py="xl">
      {/* Input Section */}
      <Paper p="md" radius="md" withBorder mb="xl">
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
      </Paper>

      {/* Report Section */}
      {report && (
        <Stack spacing="lg">
          <Group position="apart">
            <Title order={2}>Analysis Report for {report.ticker}</Title>
            <Badge size="lg" variant="filled" color={
              report.sentiment_summary === 'positive' ? 'green' :
              report.sentiment_summary === 'negative' ? 'red' : 'blue'
            }>
              {report.sentiment_summary}
            </Badge>
          </Group>

          {/* Stock Data Section */}
          <Paper withBorder p="md" radius="md">
            <Title order={3} mb="lg">Stock Data</Title>
            <Grid>
              <Grid.Col span={3}>
                <Text weight={500}>Price</Text>
                <Text size="xl">${report.stock_data.price}</Text>
              </Grid.Col>
              <Grid.Col span={3}>
                <Text weight={500}>Change</Text>
                <Text size="xl" color={report.stock_data.change.startsWith('-') ? 'red' : 'green'}>
                  {report.stock_data.change}
                </Text>
              </Grid.Col>
              <Grid.Col span={3}>
                <Text weight={500}>Market Cap</Text>
                <Text size="xl">{report.stock_data.market_cap}</Text>
              </Grid.Col>
              <Grid.Col span={3}>
                <Text weight={500}>P/E Ratio</Text>
                <Text size="xl">{report.stock_data.pe_ratio.toFixed(2)}</Text>
              </Grid.Col>
            </Grid>
          </Paper>

          {/* Key Insights Section */}
          {report.key_insights && report.key_insights.length > 0 && (
            <Paper withBorder p="md" radius="md">
              <Title order={3} mb="md">Key Insights</Title>
              <List spacing="xs">
                {report.key_insights.map((insight, index) => (
                  <List.Item key={index}>{insight}</List.Item>
                ))}
              </List>
            </Paper>
          )}

          {/* News Articles Section */}
          {report.news_articles && report.news_articles.length > 0 && (
            <Paper withBorder p="md" radius="md">
              <Group mb="md">
                <ThemeIcon size="lg" radius="md">
                  <IconNews size={20} />
                </ThemeIcon>
                <Title order={3}>Recent News</Title>
              </Group>
              <Stack spacing="md">
                {report.news_articles.map((article, index) => (
                  <Card key={index} withBorder padding="sm">
                    <Group position="apart" mb="xs">
                      <Text weight={500}>{article.headline}</Text>
                      <Badge color={
                        article.sentiment === 'positive' ? 'green' :
                        article.sentiment === 'negative' ? 'red' : 'blue'
                      }>
                        {article.sentiment}
                      </Badge>
                    </Group>
                    <Text size="sm" color="dimmed" mb="xs">{article.summary}</Text>
                    <Group position="apart">
                      <Text component="a" href={article.url} target="_blank" size="sm" color="blue">
                        Read More
                      </Text>
                      <Text size="xs" color="dimmed">
                        {formatDate(article.published_at)}
                      </Text>
                    </Group>
                  </Card>
                ))}
              </Stack>
            </Paper>
          )}

          {/* YouTube Videos Section */}
          {report.youtube_videos && report.youtube_videos.length > 0 && (
            <Paper withBorder p="md" radius="md">
              <Group mb="md">
                <ThemeIcon size="lg" radius="md">
                  <IconBrandYoutube size={20} />
                </ThemeIcon>
                <Title order={3}>Related Videos</Title>
              </Group>
              <Stack spacing="md">
                {report.youtube_videos.map((video, index) => (
                  <Card key={index} withBorder padding="sm">
                    <Text component="a" href={video.url} target="_blank">
                      {video.title}
                    </Text>
                  </Card>
                ))}
              </Stack>
            </Paper>
          )}
        </Stack>
      )}
    </Container>
  );
}