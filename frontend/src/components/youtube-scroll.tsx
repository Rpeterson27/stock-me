import type React from "react"
import { Paper, Title, Text, ScrollArea } from "@mantine/core"
import styles from "./YouTubeScroll.module.css"

interface Video {
  title: string
  url: string
  summary: string
  channel: string
  published_at: string
}

interface YouTubeScrollProps {
  videos: Video[]
}

const YouTubeScroll: React.FC<YouTubeScrollProps> = ({ videos }) => {
  return (
    <Paper shadow="md" p="xl" className={styles.container}>
      <Title order={3} mb="md" className={styles.title}>
        Related YouTube Videos
      </Title>
      <ScrollArea style={{ height: 400 }}>
        {videos.map((video, index) => (
          <div key={index} className={styles.videoItem}>
            <img
              src={`https://via.placeholder.com/120x90.png?text=Video+${index + 1}`}
              alt={video.title}
              className={styles.thumbnail}
            />
            <div>
              <Text size="sm" fw={500}>
                {video.title}
              </Text>
              <Text size="xs" c="dimmed">
                {video.channel}
              </Text>
              <Text size="xs" c="dimmed">
                {new Date(video.published_at).toLocaleDateString()}
              </Text>
              <Text size="xs" mt="xs">
                {video.summary}
              </Text>
            </div>
          </div>
        ))}
      </ScrollArea>
    </Paper>
  )
}

export default YouTubeScroll
