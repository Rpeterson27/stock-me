import React from 'react';
import { Paper, Title, Text, List, Group, Badge, useMantineTheme, Accordion, Box } from '@mantine/core';
import { ChartLine, ChartBar, MessageCircle2, AlertTriangle, Target } from 'tabler-icons-react';

interface AnalysisSection {
  title: string;
  content: string[];
  type: 'technical' | 'fundamental' | 'sentiment' | 'risks' | 'opportunities';
}

interface StockAnalysisProps {
  sections: AnalysisSection[];
}

const StockAnalysis: React.FC<StockAnalysisProps> = ({ sections }) => {
  const theme = useMantineTheme();

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'technical':
        return theme.colors.blue?.[6] || '#1976D2';
      case 'fundamental':
        return theme.colors.green?.[6] || '#388E3C';
      case 'sentiment':
        return theme.colors.yellow?.[6] || '#FFA000';
      case 'risks':
        return theme.colors.red?.[6] || '#D32F2F';
      case 'opportunities':
        return theme.colors.teal?.[6] || '#388E3C';
      default:
        return theme.colors.gray?.[6] || '#1976D2';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'technical':
        return <ChartLine size={20} />;
      case 'fundamental':
        return <ChartBar size={20} />;
      case 'sentiment':
        return <MessageCircle2 size={20} />;
      case 'risks':
        return <AlertTriangle size={20} />;
      case 'opportunities':
        return <Target size={20} />;
      default:
        return null;
    }
  };

  if (!sections || sections.length === 0) {
    return (
      <Paper shadow="md" p="xl" style={{ marginTop: '1rem' }}>
        <Text c="dimmed" ta="center">No analysis available</Text>
      </Paper>
    );
  }

  return (
    <Paper shadow="md" p="xl" style={{ marginTop: '1rem' }}>
      <Title order={3} mb="xl" style={{ color: theme.colors.gray[8] }}>
        Full Analysis
      </Title>
      
      <Accordion multiple defaultValue={['Technical Analysis']}>
        {sections.map((section, index) => (
          <Accordion.Item key={index} value={section.title}>
            <Accordion.Control>
              <Group justify="space-between" align="center">
                <Group>
                  {getTypeIcon(section.type)}
                  <Title order={4}>{section.title}</Title>
                </Group>
                <Badge 
                  size="lg"
                  style={{ 
                    backgroundColor: getTypeColor(section.type),
                    color: 'white',
                    textTransform: 'capitalize'
                  }}
                >
                  {section.type}
                </Badge>
              </Group>
            </Accordion.Control>
            <Accordion.Panel>
              <List spacing="md" size="md" style={{ color: theme.colors.gray[7] }}>
                {section.content.map((point, i) => (
                  <List.Item key={i}>
                    <Text size="sm">{point}</Text>
                  </List.Item>
                ))}
              </List>
            </Accordion.Panel>
          </Accordion.Item>
        ))}
      </Accordion>
    </Paper>
  );
};

export default StockAnalysis;
