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

  if (!user.name || typeof user.name !== 'string' || user.name.trim().length < 2) {
    errors.push('Name must be a string with at least 2 characters');
  }

  if (!user.email || typeof user.email !== 'string' || !user.email.includes('@')) {
    errors.push('Valid email is required');
  }

  if (user.role && !['admin', 'user'].includes(user.role)) {
    errors.push('Role must be either "admin" or "user"');
  }

  return { valid: errors.length === 0, errors };
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const role = searchParams.get('role');

  let filteredUsers = dummyUsers;

  if (role) {
    filteredUsers = dummyUsers.filter(user => user.role === role);
  }

  return NextResponse.json(filteredUsers);
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const validation = validateUser(body);

    if (!validation.valid) {
      return NextResponse.json({ error: 'Validation failed', details: validation.errors }, { status: 400 });
    }

    const newUser: User = {
      id: dummyUsers.length + 1,
      name: body.name.trim(),
      email: body.email.toLowerCase(),
      role: body.role || 'user',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    // Check for duplicate email
    if (dummyUsers.some(u => u.email === newUser.email)) {
      return NextResponse.json({ error: 'Email already exists' }, { status: 409 });
    }

    dummyUsers.push(newUser);
    return NextResponse.json(newUser, { status: 201 });
  } catch (error) {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 });
  }
}
