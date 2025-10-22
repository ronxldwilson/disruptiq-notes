import { NextRequest, NextResponse } from 'next/server';

interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  categoryId: number;
  stock: number;
  createdAt: string;
  updatedAt: string;
  active: boolean;
}

const dummyProducts: Product[] = [
  {
    id: 1,
    name: 'Laptop Pro',
    description: 'High-performance laptop for professionals',
    price: 1299.99,
    categoryId: 1,
    stock: 50,
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-01-15T10:00:00Z',
    active: true
  },
  {
    id: 2,
    name: 'Wireless Headphones',
    description: 'Noise-cancelling wireless headphones',
    price: 199.99,
    categoryId: 2,
    stock: 100,
    createdAt: '2024-01-16T11:30:00Z',
    updatedAt: '2024-01-16T11:30:00Z',
    active: true
  },
  {
    id: 3,
    name: 'Smartphone Case',
    description: 'Protective case for smartphones',
    price: 29.99,
    categoryId: 3,
    stock: 200,
    createdAt: '2024-01-17T14:20:00Z',
    updatedAt: '2024-01-17T14:20:00Z',
    active: true
  },
];

function validateProduct(product: Partial<Product>): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!product.name || typeof product.name !== 'string' || product.name.trim().length < 2) {
    errors.push('Name must be a string with at least 2 characters');
  }

  if (!product.description || typeof product.description !== 'string' || product.description.trim().length < 10) {
    errors.push('Description must be a string with at least 10 characters');
  }

  if (product.price !== undefined && (typeof product.price !== 'number' || product.price <= 0)) {
    errors.push('Price must be a positive number');
  }

  if (product.categoryId !== undefined && (typeof product.categoryId !== 'number' || product.categoryId <= 0)) {
    errors.push('Category ID must be a positive number');
  }

  if (product.stock !== undefined && (typeof product.stock !== 'number' || product.stock < 0)) {
    errors.push('Stock must be a non-negative number');
  }

  if (product.active !== undefined && typeof product.active !== 'boolean') {
    errors.push('Active must be a boolean');
  }

  return { valid: errors.length === 0, errors };
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const categoryId = searchParams.get('categoryId');
  const minPrice = searchParams.get('minPrice');
  const maxPrice = searchParams.get('maxPrice');
  const active = searchParams.get('active');

  let filteredProducts = dummyProducts;

  if (categoryId) {
    filteredProducts = filteredProducts.filter(product => product.categoryId === parseInt(categoryId));
  }

  if (minPrice) {
    filteredProducts = filteredProducts.filter(product => product.price >= parseFloat(minPrice));
  }

  if (maxPrice) {
    filteredProducts = filteredProducts.filter(product => product.price <= parseFloat(maxPrice));
  }

  if (active !== null) {
    filteredProducts = filteredProducts.filter(product => product.active === (active === 'true'));
  }

  return NextResponse.json(filteredProducts);
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const validation = validateProduct(body);

    if (!validation.valid) {
      return NextResponse.json({ error: 'Validation failed', details: validation.errors }, { status: 400 });
    }

    const newProduct: Product = {
      id: dummyProducts.length + 1,
      name: body.name.trim(),
      description: body.description.trim(),
      price: body.price,
      categoryId: body.categoryId,
      stock: body.stock || 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      active: body.active !== undefined ? body.active : true,
    };

    dummyProducts.push(newProduct);
    return NextResponse.json(newProduct, { status: 201 });
  } catch (error) {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 });
  }
}
