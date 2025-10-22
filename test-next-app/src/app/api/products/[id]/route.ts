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

  if (product.name !== undefined && (typeof product.name !== 'string' || product.name.trim().length < 2)) {
    errors.push('Name must be a string with at least 2 characters');
  }

  if (product.description !== undefined && (typeof product.description !== 'string' || product.description.trim().length < 10)) {
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

export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  const { id } = params;
  const productId = parseInt(id);

  if (isNaN(productId)) {
    return NextResponse.json({ error: 'Invalid product ID' }, { status: 400 });
  }

  const product = dummyProducts.find(p => p.id === productId);

  if (!product) {
    return NextResponse.json({ error: 'Product not found' }, { status: 404 });
  }

  return NextResponse.json(product);
}

export async function PUT(request: NextRequest, { params }: { params: { id: string } }) {
  const { id } = params;
  const productId = parseInt(id);

  if (isNaN(productId)) {
    return NextResponse.json({ error: 'Invalid product ID' }, { status: 400 });
  }

  const productIndex = dummyProducts.findIndex(p => p.id === productId);

  if (productIndex === -1) {
    return NextResponse.json({ error: 'Product not found' }, { status: 404 });
  }

  try {
    const body = await request.json();
    const validation = validateProduct(body);

    if (!validation.valid) {
      return NextResponse.json({ error: 'Validation failed', details: validation.errors }, { status: 400 });
    }

    const updatedProduct = {
      ...dummyProducts[productIndex],
      ...body,
      name: body.name ? body.name.trim() : dummyProducts[productIndex].name,
      description: body.description ? body.description.trim() : dummyProducts[productIndex].description,
      updatedAt: new Date().toISOString(),
    };

    dummyProducts[productIndex] = updatedProduct;
    return NextResponse.json(updatedProduct);
  } catch (error) {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 });
  }
}

export async function DELETE(request: NextRequest, { params }: { params: { id: string } }) {
  const { id } = params;
  const productId = parseInt(id);

  if (isNaN(productId)) {
    return NextResponse.json({ error: 'Invalid product ID' }, { status: 400 });
  }

  const productIndex = dummyProducts.findIndex(p => p.id === productId);

  if (productIndex === -1) {
    return NextResponse.json({ error: 'Product not found' }, { status: 404 });
  }

  const deletedProduct = dummyProducts.splice(productIndex, 1)[0];
  return NextResponse.json({ message: 'Product deleted successfully', product: deletedProduct });
}
