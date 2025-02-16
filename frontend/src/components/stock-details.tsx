import type React from "react"
import { Paper, Title, Text, Group, Badge, Grid } from "@mantine/core"
import { TrendingUp, TrendingDown } from "tabler-icons-react"
import styles from "./StockDetails.module.css"

interface StockDetailsProps {
  price: number
  change: string
  market_cap: string
  pe_ratio: number
  sentiment: string
}

const StockDetails: React.FC<StockDetailsProps> = ({ price, change, market_cap, pe_ratio, sentiment }) => {
  const isPositive = change.startsWith("+")

  return (
    <Paper shadow="md" p="xl" className={styles.container}>
      <Grid>
        <Grid.Col span={12}>
          <Group justify="apart">
            <Title order={2}>Stock Details</Title>
            <Badge c={sentiment === "Positive" ? "green" : sentiment === "Negative" ? "red" : "yellow"} size="lg">
              {sentiment}
            </Badge>
          </Group>
        </Grid.Col>
        <Grid.Col span={6}>
          <Text size="xl" fw={700}>
            ${price.toFixed(2)}
          </Text>
          <Group gap="xs">
            <Text c={isPositive ? "green" : "red"} fw={700}>
              {isPositive ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
              {change}
            </Text>
          </Group>
        </Grid.Col>
        <Grid.Col span={6}>
          <Text>Market Cap: {market_cap}</Text>
          <Text>P/E Ratio: {pe_ratio.toFixed(2)}</Text>
        </Grid.Col>
      </Grid>
    </Paper>
  )
}

export default StockDetails
