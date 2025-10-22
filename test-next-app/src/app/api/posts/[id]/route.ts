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

  if (post.title !== undefined && (typeof post.title !== 'string' || post.title.trim().length < 3)) {
    errors.push('Title must be a string with at least 3 characters');
  }

  if (post.content !== undefined && (typeof post.content !== 'string' || post.content.trim().length < 10)) {
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

export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  const { id } = params;
  const postId = parseInt(id);

  if (isNaN(postId)) {
    return NextResponse.json({ error: 'Invalid post ID' }, { status: 400 });
  }

  const post = dummyPosts.find(p => p.id === postId);

  if (!post) {
    return NextResponse.json({ error: 'Post not found' }, { status: 404 });
  }

  return NextResponse.json(post);
}

export async function PUT(request: NextRequest, { params }: { params: { id: string } }) {
  const { id } = params;
  const postId = parseInt(id);

  if (isNaN(postId)) {
    return NextResponse.json({ error: 'Invalid post ID' }, { status: 400 });
  }

  const postIndex = dummyPosts.findIndex(p => p.id === postId);

  if (postIndex === -1) {
    return NextResponse.json({ error: 'Post not found' }, { status: 404 });
  }

  try {
    const body = await request.json();
    const validation = validatePost(body);

    if (!validation.valid) {
      return NextResponse.json({ error: 'Validation failed', details: validation.errors }, { status: 400 });
    }

    const updatedPost = {
      ...dummyPosts[postIndex],
      ...body,
      title: body.title ? body.title.trim() : dummyPosts[postIndex].title,
      content: body.content ? body.content.trim() : dummyPosts[postIndex].content,
      updatedAt: new Date().toISOString(),
    };

    dummyPosts[postIndex] = updatedPost;
    return NextResponse.json(updatedPost);
  } catch (error) {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 });
  }
}

export async function DELETE(request: NextRequest, { params }: { params: { id: string } }) {
  const { id } = params;
  const postId = parseInt(id);

  if (isNaN(postId)) {
    return NextResponse.json({ error: 'Invalid post ID' }, { status: 400 });
  }

  const postIndex = dummyPosts.findIndex(p => p.id === postId);

  if (postIndex === -1) {
    return NextResponse.json({ error: 'Post not found' }, { status: 404 });
  }

  const deletedPost = dummyPosts.splice(postIndex, 1)[0];
  return NextResponse.json({ message: 'Post deleted successfully', post: deletedPost });
}
