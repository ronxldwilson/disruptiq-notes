import { NextRequest, NextResponse } from 'next/server';

interface OrderItem {
  id: number;
  productId: number;
  quantity: number;
  price: number;
}

interface Order {
  id: number;
  userId: number;
  items: OrderItem[];
  totalAmount: number;
  status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  createdAt: string;
  updatedAt: string;
}

const dummyOrders: Order[] = [
  {
    id: 1,
    userId: 1,
    items: [
      { id: 1, productId: 1, quantity: 1, price: 1299.99 },
      { id: 2, productId: 2, quantity: 2, price: 199.99 }
    ],
    totalAmount: 1699.97,
    status: 'delivered',
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-01-20T14:00:00Z'
  },
  {
    id: 2,
    userId: 2,
    items: [
      { id: 3, productId: 3, quantity: 1, price: 29.99 }
    ],
    totalAmount: 29.99,
    status: 'pending',
    createdAt: '2024-01-18T11:30:00Z',
    updatedAt: '2024-01-18T11:30:00Z'
  },
];

function validateOrder(order: Partial<Order>): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (order.userId !== undefined && (typeof order.userId !== 'number' || order.userId <= 0)) {
    errors.push('User ID must be a positive number');
  }

  if (order.items !== undefined) {
    if (!Array.isArray(order.items)) {
      errors.push('Items must be an array');
    } else {
      order.items.forEach((item, index) => {
        if (typeof item.productId !== 'number' || item.productId <= 0) {
          errors.push(`Item ${index + 1}: Product ID must be a positive number`);
        }
        if (typeof item.quantity !== 'number' || item.quantity <= 0) {
          errors.push(`Item ${index + 1}: Quantity must be a positive number`);
        }
        if (typeof item.price !== 'number' || item.price <= 0) {
          errors.push(`Item ${index + 1}: Price must be a positive number`);
        }
      });
    }
  }

  if (order.status !== undefined && !['pending', 'processing', 'shipped', 'delivered', 'cancelled'].includes(order.status)) {
    errors.push('Status must be one of: pending, processing, shipped, delivered, cancelled');
  }

  return { valid: errors.length === 0, errors };
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const userId = searchParams.get('userId');
  const status = searchParams.get('status');

  let filteredOrders = dummyOrders;

  if (userId) {
    filteredOrders = filteredOrders.filter(order => order.userId === parseInt(userId));
  }

  if (status) {
    filteredOrders = filteredOrders.filter(order => order.status === status);
  }

  return NextResponse.json(filteredOrders);
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const validation = validateOrder(body);

    if (!validation.valid) {
      return NextResponse.json({ error: 'Validation failed', details: validation.errors }, { status: 400 });
    }

    // Calculate total amount if not provided
    let totalAmount = body.totalAmount;
    if (totalAmount === undefined && body.items) {
      totalAmount = body.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    }

    const newOrder: Order = {
      id: dummyOrders.length + 1,
      userId: body.userId,
      items: body.items.map((item, index) => ({
        id: Date.now() + index, // Simple ID generation
        productId: item.productId,
        quantity: item.quantity,
        price: item.price
      })),
      totalAmount: totalAmount,
      status: body.status || 'pending',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    dummyOrders.push(newOrder);
    return NextResponse.json(newOrder, { status: 201 });
  } catch (error) {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 });
  }
}
