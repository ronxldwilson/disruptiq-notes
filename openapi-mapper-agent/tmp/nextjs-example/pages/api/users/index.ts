import type { NextApiRequest, NextApiResponse } from 'next'

type User = {
  id: number
  name: string
}

const users: User[] = [
  { id: 1, name: 'John Doe' },
  { id: 2, name: 'Jane Doe' },
]

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse<User[] | User>
) {
  if (req.method === 'GET') {
    res.status(200).json(users)
  } else if (req.method === 'POST') {
    const newUser: User = req.body
    users.push(newUser)
    res.status(201).json(newUser)
  }
}
