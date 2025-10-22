import { NextRequest, NextResponse } from 'next/server';

interface Post {
  id: number;
  title: string;
  content: string;
  authorId: number;
  tags: string[];
  createdAt: string;
  updatedAt: string;
  published: boolean;
}

const dummyPosts: Post[] = [
  {
    id: 1,
    title: 'First Post',
    content: 'This is the content of the first post.',
    authorId: 1,
    tags: ['introduction', 'welcome'],
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-01-15T10:00:00Z',
    published: true
  },
  {
    id: 2,
    title: 'Second Post',
    content: 'This is the content of the second post.',
    authorId: 2,
    tags: ['tutorial', 'guide'],
    createdAt: '2024-01-16T11:30:00Z',
    updatedAt: '2024-01-16T11:30:00Z',
    published: true
  },
];

function validatePost(post: Partial<Post>): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!post.title || typeof post.title !== 'string' || post.title.trim().length < 3) {
    errors.push('Title must be a string with at least 3 characters');
  }

  if (!post.content || typeof post.content !== 'string' || post.content.trim().length < 10) {
    errors.push('Content must be a string with at least 10 characters');
  }

  if (post.authorId !== undefined && (typeof post.authorId !== 'number' || post.authorId <= 0)) {
    errors.push('Author ID must be a positive number');
  }

  if (post.tags !== undefined && (!Array.isArray(post.tags) || !post.tags.every(tag => typeof tag === 'string'))) {
    errors.push('Tags must be an array of strings');
  }

  if (post.published !== undefined && typeof post.published !== 'boolean') {
    errors.push('Published must be a boolean');
  }

  return { valid: errors.length === 0, errors };
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const authorId = searchParams.get('authorId');
  const tag = searchParams.get('tag');
  const published = searchParams.get('published');

  let filteredPosts = dummyPosts;

  if (authorId) {
    filteredPosts = filteredPosts.filter(post => post.authorId === parseInt(authorId));
  }

  if (tag) {
    filteredPosts = filteredPosts.filter(post => post.tags.includes(tag));
  }

  if (published !== null) {
    filteredPosts = filteredPosts.filter(post => post.published === (published === 'true'));
  }

  return NextResponse.json(filteredPosts);
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const validation = validatePost(body);

    if (!validation.valid) {
      return NextResponse.json({ error: 'Validation failed', details: validation.errors }, { status: 400 });
    }

    const newPost: Post = {
      id: dummyPosts.length + 1,
      title: body.title.trim(),
      content: body.content.trim(),
      authorId: body.authorId,
      tags: body.tags || [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      published: body.published !== undefined ? body.published : false,
    };

    dummyPosts.push(newPost);
    return NextResponse.json(newPost, { status: 201 });
  } catch (error) {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 });
  }
}
