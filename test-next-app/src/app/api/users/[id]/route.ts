import { NextRequest, NextResponse } from 'next/server';

interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'user';
  createdAt: string;
  updatedAt: string;
}

const dummyUsers: User[] = [
  {
    id: 1,
    name: 'Alice Johnson',
    email: 'alice@example.com',
    role: 'admin',
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-01-15T10:00:00Z'
  },
  {
    id: 2,
    name: 'Bob Smith',
    email: 'bob@example.com',
    role: 'user',
    createdAt: '2024-01-16T11:30:00Z',
    updatedAt: '2024-01-16T11:30:00Z'
  },
  {
    id: 3,
    name: 'Charlie Brown',
    email: 'charlie@example.com',
    role: 'user',
    createdAt: '2024-01-17T14:20:00Z',
    updatedAt: '2024-01-17T14:20:00Z'
  },
];

function validateUser(user: Partial<User>): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (user.name !== undefined && (typeof user.name !== 'string' || user.name.trim().length < 2)) {
    errors.push('Name must be a string with at least 2 characters');
  }

  if (user.email !== undefined && (typeof user.email !== 'string' || !user.email.includes('@'))) {
    errors.push('Valid email is required');
  }

  if (user.role !== undefined && !['admin', 'user'].includes(user.role)) {
    errors.push('Role must be either "admin" or "user"');
  }

  return { valid: errors.length === 0, errors };
}

export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  const { id } = params;
  const userId = parseInt(id);

  if (isNaN(userId)) {
    return NextResponse.json({ error: 'Invalid user ID' }, { status: 400 });
  }

  const user = dummyUsers.find(u => u.id === userId);

  if (!user) {
    return NextResponse.json({ error: 'User not found' }, { status: 404 });
  }

  return NextResponse.json(user);
}

export async function PUT(request: NextRequest, { params }: { params: { id: string } }) {
  const { id } = params;
  const userId = parseInt(id);

  if (isNaN(userId)) {
    return NextResponse.json({ error: 'Invalid user ID' }, { status: 400 });
  }

  const userIndex = dummyUsers.findIndex(u => u.id === userId);

  if (userIndex === -1) {
    return NextResponse.json({ error: 'User not found' }, { status: 404 });
  }

  try {
    const body = await request.json();
    const validation = validateUser(body);

    if (!validation.valid) {
      return NextResponse.json({ error: 'Validation failed', details: validation.errors }, { status: 400 });
    }

    // Check for duplicate email if email is being updated
    if (body.email && body.email.toLowerCase() !== dummyUsers[userIndex].email) {
      if (dummyUsers.some(u => u.email === body.email.toLowerCase())) {
        return NextResponse.json({ error: 'Email already exists' }, { status: 409 });
      }
    }

    const updatedUser = {
      ...dummyUsers[userIndex],
      ...body,
      name: body.name ? body.name.trim() : dummyUsers[userIndex].name,
      email: body.email ? body.email.toLowerCase() : dummyUsers[userIndex].email,
      updatedAt: new Date().toISOString(),
    };

    dummyUsers[userIndex] = updatedUser;
    return NextResponse.json(updatedUser);
  } catch (error) {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 });
  }
}

export async function DELETE(request: NextRequest, { params }: { params: { id: string } }) {
  const { id } = params;
  const userId = parseInt(id);

  if (isNaN(userId)) {
    return NextResponse.json({ error: 'Invalid user ID' }, { status: 400 });
  }

  const userIndex = dummyUsers.findIndex(u => u.id === userId);

  if (userIndex === -1) {
    return NextResponse.json({ error: 'User not found' }, { status: 404 });
  }

  const deletedUser = dummyUsers.splice(userIndex, 1)[0];
  return NextResponse.json({ message: 'User deleted successfully', user: deletedUser });
}
