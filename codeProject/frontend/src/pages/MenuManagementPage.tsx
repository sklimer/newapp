import React, { useState, useEffect } from 'react';
import { menuApi } from '../api/api';
import { Category, Product } from '../types/types';



const MenuManagementPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'categories' | 'products'>('categories');
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [newCategory, setNewCategory] = useState<Omit<Category, 'id'>>({
    name: '',
    description: '',
    image_url: '',
    position: 0,
    is_active: true,
    is_stop_list: false
  });
  const [newProduct, setNewProduct] = useState<Omit<Product, 'id'>>({
    name: '',
    description: '',
    price: 0,
    discount_price: 0,
    weight: 0,
    preparation_time: 0,
    ingredients: '',
    image_url: '',
    category_id: 0,
    is_active: true,
    is_stop_list: false,
    is_recommended: false,
    is_new: false
  });


};

export default MenuManagementPage;