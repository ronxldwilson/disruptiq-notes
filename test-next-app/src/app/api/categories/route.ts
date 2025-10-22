import { NextRequest, NextResponse } from 'next/server';

interface Category {
  id: number;
  name: string;
  description: string;
  createdAt: string;
  updatedAt: string;
  active: boolean;
}

const dummyCategories: Category[] = [
  {
    id: 1,
    name: 'Electronics',
    description: 'Electronic devices and accessories',
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-01-15T10:00:00Z',
    active: true
  },
  {
    id: 2,
    name: 'Audio',
    description: 'Audio equipment and headphones',
    createdAt: '2024-01-16T11:30:00Z',
    updatedAt: '2024-01-16T11:30:00Z',
    active: true
  },
  {
    id: 3,
    name: 'Accessories',
    description: 'Phone cases and other accessories',
    createdAt: '2024-01-17T14:20:00Z',
    updatedAt: '2024-01-17T14:20:00Z',
    active: true
  },
];

function validateCategory(category: Partial<Category>): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!category.name || typeof category.name !== 'string' || category.name.trim().length < 2) {
    errors.push('Name must be a string with at least 2 characters');
  }

  if (!category.description || typeof category.description !== 'string' || category.description.trim().length < 5) {
    errors.push('Description must be a string with at least 5 characters');
  }

  if (category.active !== undefined && typeof category.active !== 'boolean') {
    errors.push('Active must be a boolean');
  }

  return { valid: errors.length === 0, errors };
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const active = searchParams.get('active');

  let filteredCategories = dummyCategories;

  if (active !== null) {
    filteredCategories = dummyCategories.filter(category => category.active === (active === 'true'));
  }

  return NextResponse.json(filteredCategories);
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const validation = validateCategory(body);

    if (!validation.valid) {
      return NextResponse.json({ error: 'Validation failed', details: validation.errors }, { status: 400 });
    }

    const newCategory: Category = {
      id: dummyCategories.length + 1,
      name: body.name.trim(),
      description: body.description.trim(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      active: body.active !== undefined ? body.active : true,
    };

    dummyCategories.push(newCategory);
    return NextResponse.json(newCategory, { status: 201 });
  } catch (error) {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 });
  }
}
