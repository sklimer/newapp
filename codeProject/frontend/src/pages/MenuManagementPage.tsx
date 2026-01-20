--- codeProject/frontend/src/pages/MenuManagementPage.tsx (原始)
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

  useEffect(() => {
    loadCategories();
    loadProducts();
  }, []);

  const loadCategories = async () => {
    try {
      const response = await menuApi.getCategories();
      // Extract the actual data from the response
      // The response object typically has a 'data' property containing the actual payload
      const data = response.data;
      // Ensure we're working with an array
      const categoriesData = Array.isArray(data) ? data : (data?.categories || []);
      setCategories(categoriesData);
    } catch (error) {
      console.error('Error loading categories:', error);
      setCategories([]); // Ensure categories is always an array
    }
  };

  const loadProducts = async () => {
    try {
      const response = await menuApi.getProducts();
      // Extract the actual data from the response
      const data = response.data;
      // Ensure we're working with an array
      const productsData = Array.isArray(data) ? data : (data?.products || []);
      setProducts(productsData);
    } catch (error) {
      console.error('Error loading products:', error);
      setProducts([]); // Ensure products is always an array
    }
  };

  const handleCreateCategory = async () => {
    try {
      await menuApi.createCategory(newCategory);
      setNewCategory({
        name: '',
        description: '',
        image_url: '',
        position: 0,
        is_active: true,
        is_stop_list: false
      });
      loadCategories();
    } catch (error) {
      console.error('Error creating category:', error);
    }
  };

  const handleUpdateCategory = async () => {
    if (!editingCategory) return;
    try {
      await menuApi.updateCategory(editingCategory.id, editingCategory);
      setEditingCategory(null);
      loadCategories();
    } catch (error) {
      console.error('Error updating category:', error);
    }
  };

  const handleDeleteCategory = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this category?')) {
      try {
        await menuApi.deleteCategory(id);
        loadCategories();
      } catch (error) {
        console.error('Error deleting category:', error);
      }
    }
  };

  const handleCreateProduct = async () => {
    try {
      await menuApi.createProduct(newProduct);
      setNewProduct({
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
      loadProducts();
    } catch (error) {
      console.error('Error creating product:', error);
    }
  };

  const handleUpdateProduct = async () => {
    if (!editingProduct) return;
    try {
      await menuApi.updateProduct(editingProduct.id, editingProduct);
      setEditingProduct(null);
      loadProducts();
    } catch (error) {
      console.error('Error updating product:', error);
    }
  };

  const handleDeleteProduct = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await menuApi.deleteProduct(id);
        loadProducts();
      } catch (error) {
        console.error('Error deleting product:', error);
      }
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Menu Management</h1>

      {/* Tabs */}
      <div className="flex border-b mb-6">
        <button
          className={`py-2 px-4 font-semibold ${activeTab === 'categories' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500'}`}
          onClick={() => setActiveTab('categories')}
        >
          Categories
        </button>
        <button
          className={`py-2 px-4 font-semibold ${activeTab === 'products' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500'}`}
          onClick={() => setActiveTab('products')}
        >
          Products
        </button>
      </div>

      {/* Categories Tab */}
      {activeTab === 'categories' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Add/Edit Category Form */}
          <div className="lg:col-span-1 bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4 pb-2 border-b">
              {editingCategory ? 'Edit Category' : 'Add New Category'}
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                <input
                  type="text"
                  className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                  value={editingCategory ? editingCategory.name : newCategory.name}
                  onChange={(e) =>
                    editingCategory
                      ? setEditingCategory({...editingCategory, name: e.target.value})
                      : setNewCategory({...newCategory, name: e.target.value})
                  }
                  placeholder="Enter category name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                  rows={3}
                  value={editingCategory ? editingCategory.description : newCategory.description}
                  onChange={(e) =>
                    editingCategory
                      ? setEditingCategory({...editingCategory, description: e.target.value})
                      : setNewCategory({...newCategory, description: e.target.value})
                  }
                  placeholder="Enter category description"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Image URL</label>
                <input
                  type="text"
                  className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                  value={editingCategory ? editingCategory.image_url : newCategory.image_url}
                  onChange={(e) =>
                    editingCategory
                      ? setEditingCategory({...editingCategory, image_url: e.target.value})
                      : setNewCategory({...newCategory, image_url: e.target.value})
                  }
                  placeholder="Enter image URL"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Position</label>
                <input
                  type="number"
                  min="0"
                  className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                  value={editingCategory ? editingCategory.position : newCategory.position}
                  onChange={(e) =>
                    editingCategory
                      ? setEditingCategory({...editingCategory, position: parseInt(e.target.value)})
                      : setNewCategory({...newCategory, position: parseInt(e.target.value)})
                  }
                  placeholder="Enter position number"
                />
              </div>
              
              <div className="pt-2">
                <div className="flex items-center space-x-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      checked={editingCategory ? editingCategory.is_active : newCategory.is_active}
                      onChange={(e) =>
                        editingCategory
                          ? setEditingCategory({...editingCategory, is_active: e.target.checked})
                          : setNewCategory({...newCategory, is_active: e.target.checked})
                      }
                    />
                    <span className="ml-2 text-sm text-gray-700">Active</span>
                  </label>
                  
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      checked={editingCategory ? editingCategory.is_stop_list : newCategory.is_stop_list}
                      onChange={(e) =>
                        editingCategory
                          ? setEditingCategory({...editingCategory, is_stop_list: e.target.checked})
                          : setNewCategory({...newCategory, is_stop_list: e.target.checked})
                      }
                    />
                    <span className="ml-2 text-sm text-gray-700">Stop List</span>
                  </label>
                </div>
              </div>
              
              <div className="pt-4">
                <div className="flex space-x-3">
                  {editingCategory ? (
                    <>
                      <button
                        className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors"
                        onClick={handleUpdateCategory}
                      >
                        Update
                      </button>
                      <button
                        className="flex-1 bg-gray-500 text-white py-2 px-4 rounded-md hover:bg-gray-600 transition-colors"
                        onClick={() => setEditingCategory(null)}
                      >
                        Cancel
                      </button>
                    </>
                  ) : (
                    <button
                      className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
                      onClick={handleCreateCategory}
                    >
                      Add Category
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Categories List */}
          <div className="lg:col-span-2">
            <h3 className="text-lg font-medium mb-4">Categories List</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {categories && Array.isArray(categories) ? (
                categories.map((category) => (
                  <div key={category.id} className="bg-white p-4 rounded-lg shadow border border-gray-200">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-semibold text-lg text-gray-900">{category.name}</h3>
                        <p className="text-gray-600 text-sm mt-1">{category.description}</p>
                        <div className="mt-2 text-xs text-gray-500">
                          Position: {category.position} | 
                          Status: {category.is_active ? 'Active' : 'Inactive'} | 
                          Stop List: {category.is_stop_list ? 'Yes' : 'No'}
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          className="text-blue-600 hover:text-blue-800"
                          onClick={() => setEditingCategory(category)}
                        >
                          Edit
                        </button>
                        <button
                          className="text-red-600 hover:text-red-800"
                          onClick={() => handleDeleteCategory(category.id)}
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-4 col-span-2">Loading categories...</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Products Tab */}
      {activeTab === 'products' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Add/Edit Product Form */}
          <div className="lg:col-span-1 bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4 pb-2 border-b">
              {editingProduct ? 'Edit Product' : 'Add New Product'}
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                <input
                  type="text"
                  className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                  value={editingProduct ? editingProduct.name : newProduct.name}
                  onChange={(e) =>
                    editingProduct
                      ? setEditingProduct({...editingProduct, name: e.target.value})
                      : setNewProduct({...newProduct, name: e.target.value})
                  }
                  placeholder="Enter product name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                  rows={3}
                  value={editingProduct ? editingProduct.description : newProduct.description}
                  onChange={(e) =>
                    editingProduct
                      ? setEditingProduct({...editingProduct, description: e.target.value})
                      : setNewProduct({...newProduct, description: e.target.value})
                  }
                  placeholder="Enter product description"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Price *</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                    value={editingProduct ? editingProduct.price : newProduct.price}
                    onChange={(e) =>
                      editingProduct
                        ? setEditingProduct({...editingProduct, price: parseFloat(e.target.value)})
                        : setNewProduct({...newProduct, price: parseFloat(e.target.value)})
                    }
                    placeholder="0.00"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Discount Price</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                    value={editingProduct ? editingProduct.discount_price : newProduct.discount_price}
                    onChange={(e) =>
                      editingProduct
                        ? setEditingProduct({...editingProduct, discount_price: parseFloat(e.target.value)})
                        : setNewProduct({...newProduct, discount_price: parseFloat(e.target.value)})
                    }
                    placeholder="0.00"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Weight (g)</label>
                  <input
                    type="number"
                    min="0"
                    className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                    value={editingProduct ? editingProduct.weight : newProduct.weight}
                    onChange={(e) =>
                      editingProduct
                        ? setEditingProduct({...editingProduct, weight: parseFloat(e.target.value)})
                        : setNewProduct({...newProduct, weight: parseFloat(e.target.value)})
                    }
                    placeholder="0"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Prep Time (min)</label>
                  <input
                    type="number"
                    min="0"
                    className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                    value={editingProduct ? editingProduct.preparation_time : newProduct.preparation_time}
                    onChange={(e) =>
                      editingProduct
                        ? setEditingProduct({...editingProduct, preparation_time: parseInt(e.target.value)})
                        : setNewProduct({...newProduct, preparation_time: parseInt(e.target.value)})
                    }
                    placeholder="0"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Ingredients</label>
                <textarea
                  className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                  rows={2}
                  value={editingProduct ? editingProduct.ingredients : newProduct.ingredients}
                  onChange={(e) =>
                    editingProduct
                      ? setEditingProduct({...editingProduct, ingredients: e.target.value})
                      : setNewProduct({...newProduct, ingredients: e.target.value})
                  }
                  placeholder="Enter ingredients separated by commas"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Image URL</label>
                <input
                  type="text"
                  className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                  value={editingProduct ? editingProduct.image_url : newProduct.image_url}
                  onChange={(e) =>
                    editingProduct
                      ? setEditingProduct({...editingProduct, image_url: e.target.value})
                      : setNewProduct({...newProduct, image_url: e.target.value})
                  }
                  placeholder="Enter image URL"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category *</label>
                <select
                  className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                  value={editingProduct ? editingProduct.category_id : newProduct.category_id}
                  onChange={(e) =>
                    editingProduct
                      ? setEditingProduct({...editingProduct, category_id: parseInt(e.target.value)})
                      : setNewProduct({...newProduct, category_id: parseInt(e.target.value)})
                  }
                >
                  <option value="">Select Category</option>
                  {categories && Array.isArray(categories) && categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="pt-2">
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="active"
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      checked={editingProduct ? editingProduct.is_active : newProduct.is_active}
                      onChange={(e) =>
                        editingProduct
                          ? setEditingProduct({...editingProduct, is_active: e.target.checked})
                          : setNewProduct({...newProduct, is_active: e.target.checked})
                      }
                    />
                    <label htmlFor="active" className="ml-2 text-sm text-gray-700">Active</label>
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="stopList"
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      checked={editingProduct ? editingProduct.is_stop_list : newProduct.is_stop_list}
                      onChange={(e) =>
                        editingProduct
                          ? setEditingProduct({...editingProduct, is_stop_list: e.target.checked})
                          : setNewProduct({...newProduct, is_stop_list: e.target.checked})
                      }
                    />
                    <label htmlFor="stopList" className="ml-2 text-sm text-gray-700">Stop List</label>
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="recommended"
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      checked={editingProduct ? editingProduct.is_recommended : newProduct.is_recommended}
                      onChange={(e) =>
                        editingProduct
                          ? setEditingProduct({...editingProduct, is_recommended: e.target.checked})
                          : setNewProduct({...newProduct, is_recommended: e.target.checked})
                      }
                    />
                    <label htmlFor="recommended" className="ml-2 text-sm text-gray-700">Recommended</label>
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="new"
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      checked={editingProduct ? editingProduct.is_new : newProduct.is_new}
                      onChange={(e) =>
                        editingProduct
                          ? setEditingProduct({...editingProduct, is_new: e.target.checked})
                          : setNewProduct({...newProduct, is_new: e.target.checked})
                      }
                    />
                    <label htmlFor="new" className="ml-2 text-sm text-gray-700">New</label>
                  </div>
                </div>
              </div>
              
              <div className="pt-4">
                <div className="flex space-x-3">
                  {editingProduct ? (
                    <>
                      <button
                        className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors"
                        onClick={handleUpdateProduct}
                      >
                        Update
                      </button>
                      <button
                        className="flex-1 bg-gray-500 text-white py-2 px-4 rounded-md hover:bg-gray-600 transition-colors"
                        onClick={() => setEditingProduct(null)}
                      >
                        Cancel
                      </button>
                    </>
                  ) : (
                    <button
                      className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
                      onClick={handleCreateProduct}
                    >
                      Add Product
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Products List */}
          <div className="lg:col-span-2">
            <h3 className="text-lg font-medium mb-4">Products List</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {products && categories && Array.isArray(products) && Array.isArray(categories) ? (
                products.map((product) => {
                  const category = categories.find(cat => cat.id === product.category_id);
                  return (
                    <div key={product.id} className="bg-white p-4 rounded-lg shadow border border-gray-200">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-semibold text-lg text-gray-900">{product.name}</h3>
                          <p className="text-gray-600 text-sm mt-1">{product.description}</p>
                          <div className="mt-2 flex flex-wrap gap-2 text-xs text-gray-500">
                            <span>Price: <span className="font-semibold">{product.price}</span></span>
                            {product.discount_price > 0 && <span>Disc: <span className="font-semibold">{product.discount_price}</span></span>}
                            <span>Weight: {product.weight}g</span>
                            <span>Time: {product.preparation_time}min</span>
                            <span>Category: {category?.name || 'Uncategorized'}</span>
                          </div>
                          <div className="mt-2 flex flex-wrap gap-2">
                            {product.is_active && <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">Active</span>}
                            {product.is_stop_list && <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded">Stop List</span>}
                            {product.is_recommended && <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">Recommended</span>}
                            {product.is_new && <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">New</span>}
                          </div>
                        </div>
                        <div className="flex flex-col space-y-2">
                          <button
                            className="text-blue-600 hover:text-blue-800"
                            onClick={() => setEditingProduct(product)}
                          >
                            Edit
                          </button>
                          <button
                            className="text-red-600 hover:text-red-800"
                            onClick={() => handleDeleteProduct(product.id)}
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="text-center py-4 col-span-2">Loading products...</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MenuManagementPage;

+++ codeProject/frontend/src/pages/MenuManagementPage.tsx (修改后)
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

  useEffect(() => {
    loadCategories();
    loadProducts();
  }, []);

  const loadCategories = async () => {
    try {
      const response = await menuApi.getCategories();
      // Extract the actual data from the response
      // The response object typically has a 'data' property containing the actual payload
      const data = response.data;
      // Ensure we're working with an array
      const categoriesData = Array.isArray(data) ? data : (data?.categories || []);
      setCategories(categoriesData);
    } catch (error) {
      console.error('Error loading categories:', error);
      setCategories([]); // Ensure categories is always an array
    }
  };

  const loadProducts = async () => {
    try {
      const response = await menuApi.getProducts();
      // Extract the actual data from the response
      const data = response.data;
      // Ensure we're working with an array
      const productsData = Array.isArray(data) ? data : (data?.products || []);
      setProducts(productsData);
    } catch (error) {
      console.error('Error loading products:', error);
      setProducts([]); // Ensure products is always an array
    }
  };

  const handleCreateCategory = async () => {
    try {
      await menuApi.createCategory(newCategory);
      setNewCategory({
        name: '',
        description: '',
        image_url: '',
        position: 0,
        is_active: true,
        is_stop_list: false
      });
      loadCategories();
    } catch (error) {
      console.error('Error creating category:', error);
    }
  };

  const handleUpdateCategory = async () => {
    if (!editingCategory) return;
    try {
      await menuApi.updateCategory(editingCategory.id, editingCategory);
      setEditingCategory(null);
      loadCategories();
    } catch (error) {
      console.error('Error updating category:', error);
    }
  };

  const handleDeleteCategory = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this category?')) {
      try {
        await menuApi.deleteCategory(id);
        loadCategories();
      } catch (error) {
        console.error('Error deleting category:', error);
      }
    }
  };

  const handleCreateProduct = async () => {
    try {
      await menuApi.createProduct(newProduct);
      setNewProduct({
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
      loadProducts();
    } catch (error) {
      console.error('Error creating product:', error);
    }
  };

  const handleUpdateProduct = async () => {
    if (!editingProduct) return;
    try {
      await menuApi.updateProduct(editingProduct.id, editingProduct);
      setEditingProduct(null);
      loadProducts();
    } catch (error) {
      console.error('Error updating product:', error);
    }
  };

  const handleDeleteProduct = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await menuApi.deleteProduct(id);
        loadProducts();
      } catch (error) {
        console.error('Error deleting product:', error);
      }
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Menu Management</h1>

      {/* Tabs */}
      <div className="flex border-b mb-6">
        <button
          className={`py-2 px-4 font-semibold ${activeTab === 'categories' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500'}`}
          onClick={() => setActiveTab('categories')}
        >
          Categories
        </button>
        <button
          className={`py-2 px-4 font-semibold ${activeTab === 'products' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500'}`}
          onClick={() => setActiveTab('products')}
        >
          Products
        </button>
      </div>

      {/* Categories Tab */}
      {activeTab === 'categories' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Add/Edit Category Form */}
          <div className="lg:col-span-1 bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4 pb-2 border-b">
              {editingCategory ? 'Edit Category' : 'Add New Category'}
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                <input
                  type="text"
                  className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                  value={editingCategory ? editingCategory.name : newCategory.name}
                  onChange={(e) =>
                    editingCategory
                      ? setEditingCategory({...editingCategory, name: e.target.value})
                      : setNewCategory({...newCategory, name: e.target.value})
                  }
                  placeholder="Enter category name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                  rows={3}
                  value={editingCategory ? editingCategory.description : newCategory.description}
                  onChange={(e) =>
                    editingCategory
                      ? setEditingCategory({...editingCategory, description: e.target.value})
                      : setNewCategory({...newCategory, description: e.target.value})
                  }
                  placeholder="Enter category description"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Image URL</label>
                <input
                  type="text"
                  className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                  value={editingCategory ? editingCategory.image_url : newCategory.image_url}
                  onChange={(e) =>
                    editingCategory
                      ? setEditingCategory({...editingCategory, image_url: e.target.value})
                      : setNewCategory({...newCategory, image_url: e.target.value})
                  }
                  placeholder="Enter image URL"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Position</label>
                <input
                  type="number"
                  min="0"
                  className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                  value={editingCategory ? editingCategory.position : newCategory.position}
                  onChange={(e) =>
                    editingCategory
                      ? setEditingCategory({...editingCategory, position: parseInt(e.target.value)})
                      : setNewCategory({...newCategory, position: parseInt(e.target.value)})
                  }
                  placeholder="Enter position number"
                />
              </div>

              <div className="pt-2">
                <div className="flex items-center space-x-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      checked={editingCategory ? editingCategory.is_active : newCategory.is_active}
                      onChange={(e) =>
                        editingCategory
                          ? setEditingCategory({...editingCategory, is_active: e.target.checked})
                          : setNewCategory({...newCategory, is_active: e.target.checked})
                      }
                    />
                    <span className="ml-2 text-sm text-gray-700">Active</span>
                  </label>

                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      checked={editingCategory ? editingCategory.is_stop_list : newCategory.is_stop_list}
                      onChange={(e) =>
                        editingCategory
                          ? setEditingCategory({...editingCategory, is_stop_list: e.target.checked})
                          : setNewCategory({...newCategory, is_stop_list: e.target.checked})
                      }
                    />
                    <span className="ml-2 text-sm text-gray-700">Stop List</span>
                  </label>
                </div>
              </div>

              <div className="pt-4">
                <div className="flex space-x-3">
                  {editingCategory ? (
                    <>
                      <button
                        className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors"
                        onClick={handleUpdateCategory}
                      >
                        Update
                      </button>
                      <button
                        className="flex-1 bg-gray-500 text-white py-2 px-4 rounded-md hover:bg-gray-600 transition-colors"
                        onClick={() => setEditingCategory(null)}
                      >
                        Cancel
                      </button>
                    </>
                  ) : (
                    <button
                      className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
                      onClick={handleCreateCategory}
                    >
                      Add Category
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Categories List */}
          <div className="lg:col-span-2">
            <h3 className="text-lg font-medium mb-4">Categories List</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {categories && Array.isArray(categories) ? (
                categories.map((category) => (
                  <div key={category.id} className="bg-white p-4 rounded-lg shadow border border-gray-200">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-semibold text-lg text-gray-900">{category.name}</h3>
                        <p className="text-gray-600 text-sm mt-1">{category.description}</p>
                        <div className="mt-2 text-xs text-gray-500">
                          Position: {category.position} |
                          Status: {category.is_active ? 'Active' : 'Inactive'} |
                          Stop List: {category.is_stop_list ? 'Yes' : 'No'}
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          className="text-blue-600 hover:text-blue-800"
                          onClick={() => setEditingCategory(category)}
                        >
                          Edit
                        </button>
                        <button
                          className="text-red-600 hover:text-red-800"
                          onClick={() => handleDeleteCategory(category.id)}
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-4 col-span-2">Loading categories...</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Products Tab */}
      {activeTab === 'products' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Add/Edit Product Form */}
          <div className="lg:col-span-1 bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4 pb-2 border-b">
              {editingProduct ? 'Edit Product' : 'Add New Product'}
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                <input
                  type="text"
                  className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                  value={editingProduct ? editingProduct.name : newProduct.name}
                  onChange={(e) =>
                    editingProduct
                      ? setEditingProduct({...editingProduct, name: e.target.value})
                      : setNewProduct({...newProduct, name: e.target.value})
                  }
                  placeholder="Enter product name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                  rows={3}
                  value={editingProduct ? editingProduct.description : newProduct.description}
                  onChange={(e) =>
                    editingProduct
                      ? setEditingProduct({...editingProduct, description: e.target.value})
                      : setNewProduct({...newProduct, description: e.target.value})
                  }
                  placeholder="Enter product description"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Price *</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                    value={editingProduct ? editingProduct.price : newProduct.price}
                    onChange={(e) =>
                      editingProduct
                        ? setEditingProduct({...editingProduct, price: parseFloat(e.target.value)})
                        : setNewProduct({...newProduct, price: parseFloat(e.target.value)})
                    }
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Discount Price</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                    value={editingProduct ? editingProduct.discount_price : newProduct.discount_price}
                    onChange={(e) =>
                      editingProduct
                        ? setEditingProduct({...editingProduct, discount_price: parseFloat(e.target.value)})
                        : setNewProduct({...newProduct, discount_price: parseFloat(e.target.value)})
                    }
                    placeholder="0.00"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Weight (g)</label>
                  <input
                    type="number"
                    min="0"
                    className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                    value={editingProduct ? editingProduct.weight : newProduct.weight}
                    onChange={(e) =>
                      editingProduct
                        ? setEditingProduct({...editingProduct, weight: parseFloat(e.target.value)})
                        : setNewProduct({...newProduct, weight: parseFloat(e.target.value)})
                    }
                    placeholder="0"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Prep Time (min)</label>
                  <input
                    type="number"
                    min="0"
                    className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                    value={editingProduct ? editingProduct.preparation_time : newProduct.preparation_time}
                    onChange={(e) =>
                      editingProduct
                        ? setEditingProduct({...editingProduct, preparation_time: parseInt(e.target.value)})
                        : setNewProduct({...newProduct, preparation_time: parseInt(e.target.value)})
                    }
                    placeholder="0"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Ingredients</label>
                <textarea
                  className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                  rows={2}
                  value={editingProduct ? editingProduct.ingredients : newProduct.ingredients}
                  onChange={(e) =>
                    editingProduct
                      ? setEditingProduct({...editingProduct, ingredients: e.target.value})
                      : setNewProduct({...newProduct, ingredients: e.target.value})
                  }
                  placeholder="Enter ingredients separated by commas"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Image URL</label>
                <input
                  type="text"
                  className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                  value={editingProduct ? editingProduct.image_url : newProduct.image_url}
                  onChange={(e) =>
                    editingProduct
                      ? setEditingProduct({...editingProduct, image_url: e.target.value})
                      : setNewProduct({...newProduct, image_url: e.target.value})
                  }
                  placeholder="Enter image URL"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category *</label>
                <select
                  className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                  value={editingProduct ? editingProduct.category_id : newProduct.category_id}
                  onChange={(e) =>
                    editingProduct
                      ? setEditingProduct({...editingProduct, category_id: parseInt(e.target.value)})
                      : setNewProduct({...newProduct, category_id: parseInt(e.target.value)})
                  }
                >
                  <option value="">Select Category</option>
                  {categories && Array.isArray(categories) && categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="pt-2">
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="active"
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      checked={editingProduct ? editingProduct.is_active : newProduct.is_active}
                      onChange={(e) =>
                        editingProduct
                          ? setEditingProduct({...editingProduct, is_active: e.target.checked})
                          : setNewProduct({...newProduct, is_active: e.target.checked})
                      }
                    />
                    <label htmlFor="active" className="ml-2 text-sm text-gray-700">Active</label>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="stopList"
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      checked={editingProduct ? editingProduct.is_stop_list : newProduct.is_stop_list}
                      onChange={(e) =>
                        editingProduct
                          ? setEditingProduct({...editingProduct, is_stop_list: e.target.checked})
                          : setNewProduct({...newProduct, is_stop_list: e.target.checked})
                      }
                    />
                    <label htmlFor="stopList" className="ml-2 text-sm text-gray-700">Stop List</label>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="recommended"
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      checked={editingProduct ? editingProduct.is_recommended : newProduct.is_recommended}
                      onChange={(e) =>
                        editingProduct
                          ? setEditingProduct({...editingProduct, is_recommended: e.target.checked})
                          : setNewProduct({...newProduct, is_recommended: e.target.checked})
                      }
                    />
                    <label htmlFor="recommended" className="ml-2 text-sm text-gray-700">Recommended</label>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="new"
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      checked={editingProduct ? editingProduct.is_new : newProduct.is_new}
                      onChange={(e) =>
                        editingProduct
                          ? setEditingProduct({...editingProduct, is_new: e.target.checked})
                          : setNewProduct({...newProduct, is_new: e.target.checked})
                      }
                    />
                    <label htmlFor="new" className="ml-2 text-sm text-gray-700">New</label>
                  </div>
                </div>
              </div>

              <div className="pt-4">
                <div className="flex space-x-3">
                  {editingProduct ? (
                    <>
                      <button
                        className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors"
                        onClick={handleUpdateProduct}
                      >
                        Update
                      </button>
                      <button
                        className="flex-1 bg-gray-500 text-white py-2 px-4 rounded-md hover:bg-gray-600 transition-colors"
                        onClick={() => setEditingProduct(null)}
                      >
                        Cancel
                      </button>
                    </>
                  ) : (
                    <button
                      className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
                      onClick={handleCreateProduct}
                    >
                      Add Product
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Products List */}
          <div className="lg:col-span-2">
            <h3 className="text-lg font-medium mb-4">Products List</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {products && categories && Array.isArray(products) && Array.isArray(categories) ? (
                products.map((product) => {
                  const category = categories.find(cat => cat.id === product.category_id);
                  return (
                    <div key={product.id} className="bg-white p-4 rounded-lg shadow border border-gray-200">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-semibold text-lg text-gray-900">{product.name}</h3>
                          <p className="text-gray-600 text-sm mt-1">{product.description}</p>
                          <div className="mt-2 flex flex-wrap gap-2 text-xs text-gray-500">
                            <span>Price: <span className="font-semibold">{product.price}</span></span>
                            {product.discount_price > 0 && <span>Disc: <span className="font-semibold">{product.discount_price}</span></span>}
                            <span>Weight: {product.weight}g</span>
                            <span>Time: {product.preparation_time}min</span>
                            <span>Category: {category?.name || 'Uncategorized'}</span>
                          </div>
                          <div className="mt-2 flex flex-wrap gap-2">
                            {product.is_active && <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">Active</span>}
                            {product.is_stop_list && <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded">Stop List</span>}
                            {product.is_recommended && <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">Recommended</span>}
                            {product.is_new && <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">New</span>}
                          </div>
                        </div>
                        <div className="flex flex-col space-y-2">
                          <button
                            className="text-blue-600 hover:text-blue-800"
                            onClick={() => setEditingProduct(product)}
                          >
                            Edit
                          </button>
                          <button
                            className="text-red-600 hover:text-red-800"
                            onClick={() => handleDeleteProduct(product.id)}
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="text-center py-4 col-span-2">Loading products...</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MenuManagementPage;