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

  if (category.name !== undefined && (typeof category.name !== 'string' || category.name.trim().length < 2)) {
    errors.push('Name must be a string with at least 2 characters');
  }

  if (category.description !== undefined && (typeof category.description !== 'string' || category.description.trim().length < 5)) {
    errors.push('Description must be a string with at least 5 characters');
  }

  if (category.active !== undefined && typeof category.active !== 'boolean') {
    errors.push('Active must be a boolean');
  }

  return { valid: errors.length === 0, errors };
}

export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  const { id } = params;
  const categoryId = parseInt(id);

  if (isNaN(categoryId)) {
    return NextResponse.json({ error: 'Invalid category ID' }, { status: 400 });
  }

  const category = dummyCategories.find(c => c.id === categoryId);

  if (!category) {
    return NextResponse.json({ error: 'Category not found' }, { status: 404 });
  }

  return NextResponse.json(category);
}

export async function PUT(request: NextRequest, { params }: { params: { id: string } }) {
  const { id } = params;
  const categoryId = parseInt(id);

  if (isNaN(categoryId)) {
    return NextResponse.json({ error: 'Invalid category ID' }, { status: 400 });
  }

  const categoryIndex = dummyCategories.findIndex(c => c.id === categoryId);

  if (categoryIndex === -1) {
    return NextResponse.json({ error: 'Category not found' }, { status: 404 });
  }

  try {
    const body = await request.json();
    const validation = validateCategory(body);

    if (!validation.valid) {
      return NextResponse.json({ error: 'Validation failed', details: validation.errors }, { status: 400 });
    }

    const updatedCategory = {
      ...dummyCategories[categoryIndex],
      ...body,
      name: body.name ? body.name.trim() : dummyCategories[categoryIndex].name,
      description: body.description ? body.description.trim() : dummyCategories[categoryIndex].description,
      updatedAt: new Date().toISOString(),
    };

    dummyCategories[categoryIndex] = updatedCategory;
    return NextResponse.json(updatedCategory);
  } catch (error) {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 });
  }
}

export async function DELETE(request: NextRequest, { params }: { params: { id: string } }) {
  const { id } = params;
  const categoryId = parseInt(id);

  if (isNaN(categoryId)) {
    return NextResponse.json({ error: 'Invalid category ID' }, { status: 400 });
  }

  const categoryIndex = dummyCategories.findIndex(c => c.id === categoryId);

  if (categoryIndex === -1) {
    return NextResponse.json({ error: 'Category not found' }, { status: 404 });
  }

  const deletedCategory = dummyCategories.splice(categoryIndex, 1)[0];
  return NextResponse.json({ message: 'Category deleted successfully', category: deletedCategory });
}
