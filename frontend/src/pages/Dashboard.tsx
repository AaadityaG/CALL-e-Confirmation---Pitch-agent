import { AppShell } from '@/components/AppShell'
import { useGetMeQuery } from '@/services/authApi'
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

const overviewCards = [
  { title: 'Calls', description: 'AI conversations with customers' },
  { title: 'Orders', description: 'Confirmed & updated shipments' },
  { title: 'Revenue', description: 'Upsells and recovered orders' },
]

export default function Dashboard() {
  const { data } = useGetMeQuery()
  const user = data?.user

  return (
    <AppShell>
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">
          Welcome back{user ? `, ${user.name.split(' ')[0]}` : ''}
        </h1>
        <p className="text-muted-foreground">
          Your AI phone agent turns post-purchase calls into Shopify actions.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {overviewCards.map((card) => (
          <Card key={card.title}>
            <CardHeader>
              <CardTitle>{card.title}</CardTitle>
              <CardDescription>{card.description}</CardDescription>
            </CardHeader>
          </Card>
        ))}
      </div>
    </AppShell>
  )
}