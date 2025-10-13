// tmp/nestjs_app.ts
import { Controller, Get, Post, Param, Body } from '@nestjs/common';

@Controller('users')
export class UsersController {
  @Get()
  findAll(): string {
    return 'This action returns all users';
  }

  @Get(':id')
  findOne(@Param('id') id: string): string {
    return `This action returns a #${id} user`;
  }

  @Post()
  create(@Body() createUserDto: any): string {
    return 'This action adds a new user';
  }
}

@Controller('products')
export class ProductsController {
  @Get()
  findAllProducts(): string {
    return 'This action returns all products';
  }
}
