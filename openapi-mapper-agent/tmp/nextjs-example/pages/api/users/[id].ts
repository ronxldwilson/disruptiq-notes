import type { NextApiRequest, NextApiResponse } from 'next'

type User = {
  id: number
  name: string
}

let users: User[] = [
  { id: 1, name: 'John Doe' },
  { id: 2, name: 'Jane Doe' },
]

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse<User | { message: string }>
) {
  const { id } = req.query
  const userId = parseInt(id as string)

  if (req.method === 'GET') {
    const user = users.find((u) => u.id === userId)
    if (user) {
      res.status(200).json(user)
    } else {
      res.status(404).json({ message: 'User not found' })
    }
  } else if (req.method === 'PUT') {
    const updatedUser: User = req.body
    const userIndex = users.findIndex((u) => u.id === userId)
    if (userIndex !== -1) {
      users[userIndex] = updatedUser
      res.status(200).json(updatedUser)
    } else {
      res.status(404).json({ message: 'User not found' })
    }
  } else if (req.method === 'DELETE') {
    const userIndex = users.findIndex((u) => u.id === userId)
    if (userIndex !== -1) {
      users.splice(userIndex, 1)
      res.status(200).json({ message: 'User deleted' })
    } else {
      res.status(404).json({ message: 'User not found' })
    }
  }
}
