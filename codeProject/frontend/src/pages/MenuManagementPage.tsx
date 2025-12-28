import React, { useState, useEffect } from 'react';
import {
  createCategory,
  updateCategory,
  deleteCategory,
  getCategories,
  createProduct,
  updateProduct,
  deleteProduct,
  getProducts
} from '../api/api';
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
      const data = await getCategories();
      setCategories(data);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const loadProducts = async () => {
    try {
      const data = await getProducts();
      setProducts(data);
    } catch (error) {
      console.error('Error loading products:', error);
    }
  };

  const handleCreateCategory = async () => {
    try {
      await createCategory(newCategory);
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
      await updateCategory(editingCategory.id, editingCategory);
      setEditingCategory(null);
      loadCategories();
    } catch (error) {
      console.error('Error updating category:', error);
    }
  };

  const handleDeleteCategory = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this category?')) {
      try {
        await deleteCategory(id);
        loadCategories();
      } catch (error) {
        console.error('Error deleting category:', error);
      }
    }
  };

  const handleCreateProduct = async () => {
    try {
      await createProduct(newProduct);
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
      await updateProduct(editingProduct.id, editingProduct);
      setEditingProduct(null);
      loadProducts();
    } catch (error) {
      console.error('Error updating product:', error);
    }
  };

  const handleDeleteProduct = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await deleteProduct(id);
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Add/Edit Category Form */}
          <div className="bg-white p-4 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">
              {editingCategory ? 'Edit Category' : 'Add New Category'}
            </h2>
            <div className="space-y-2">
              <input
                type="text"
                placeholder="Name"
                className="w-full p-2 border rounded"
                value={editingCategory ? editingCategory.name : newCategory.name}
                onChange={(e) =>
                  editingCategory
                    ? setEditingCategory({...editingCategory, name: e.target.value})
                    : setNewCategory({...newCategory, name: e.target.value})
                }
              />
              <textarea
                placeholder="Description"
                className="w-full p-2 border rounded"
                value={editingCategory ? editingCategory.description : newCategory.description}
                onChange={(e) =>
                  editingCategory
                    ? setEditingCategory({...editingCategory, description: e.target.value})
                    : setNewCategory({...newCategory, description: e.target.value})
                }
              />
              <input
                type="text"
                placeholder="Image URL"
                className="w-full p-2 border rounded"
                value={editingCategory ? editingCategory.image_url : newCategory.image_url}
                onChange={(e) =>
                  editingCategory
                    ? setEditingCategory({...editingCategory, image_url: e.target.value})
                    : setNewCategory({...newCategory, image_url: e.target.value})
                }
              />
              <input
                type="number"
                placeholder="Position"
                className="w-full p-2 border rounded"
                value={editingCategory ? editingCategory.position : newCategory.position}
                onChange={(e) =>
                  editingCategory
                    ? setEditingCategory({...editingCategory, position: parseInt(e.target.value)})
                    : setNewCategory({...newCategory, position: parseInt(e.target.value)})
                }
              />
              <div className="flex items-center">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="mr-2"
                    checked={editingCategory ? editingCategory.is_active : newCategory.is_active}
                    onChange={(e) =>
                      editingCategory
                        ? setEditingCategory({...editingCategory, is_active: e.target.checked})
                        : setNewCategory({...newCategory, is_active: e.target.checked})
                    }
                  />
                  Active
                </label>
                <label className="flex items-center ml-4">
                  <input
                    type="checkbox"
                    className="mr-2"
                    checked={editingCategory ? editingCategory.is_stop_list : newCategory.is_stop_list}
                    onChange={(e) =>
                      editingCategory
                        ? setEditingCategory({...editingCategory, is_stop_list: e.target.checked})
                        : setNewCategory({...newCategory, is_stop_list: e.target.checked})
                    }
                  />
                  Stop List
                </label>
              </div>
              <div className="flex space-x-2">
                {editingCategory ? (
                  <>
                    <button
                      className="flex-1 bg-green-500 text-white py-2 rounded hover:bg-green-600"
                      onClick={handleUpdateCategory}
                    >
                      Update
                    </button>
                    <button
                      className="flex-1 bg-gray-500 text-white py-2 rounded hover:bg-gray-600"
                      onClick={() => setEditingCategory(null)}
                    >
                      Cancel
                    </button>
                  </>
                ) : (
                  <button
                    className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
                    onClick={handleCreateCategory}
                  >
                    Add Category
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Categories List */}
          {categories.map((category) => (
            <div key={category.id} className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-semibold text-lg">{category.name}</h3>
              <p className="text-gray-600 text-sm">{category.description}</p>
              <div className="mt-2 flex space-x-2">
                <button
                  className="text-blue-500 hover:text-blue-700"
                  onClick={() => setEditingCategory(category)}
                >
                  Edit
                </button>
                <button
                  className="text-red-500 hover:text-red-700"
                  onClick={() => handleDeleteCategory(category.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Products Tab */}
      {activeTab === 'products' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Add/Edit Product Form */}
          <div className="bg-white p-4 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">
              {editingProduct ? 'Edit Product' : 'Add New Product'}
            </h2>
            <div className="space-y-2">
              <input
                type="text"
                placeholder="Name"
                className="w-full p-2 border rounded"
                value={editingProduct ? editingProduct.name : newProduct.name}
                onChange={(e) =>
                  editingProduct
                    ? setEditingProduct({...editingProduct, name: e.target.value})
                    : setNewProduct({...newProduct, name: e.target.value})
                }
              />
              <textarea
                placeholder="Description"
                className="w-full p-2 border rounded"
                value={editingProduct ? editingProduct.description : newProduct.description}
                onChange={(e) =>
                  editingProduct
                    ? setEditingProduct({...editingProduct, description: e.target.value})
                    : setNewProduct({...newProduct, description: e.target.value})
                }
              />
              <input
                type="number"
                placeholder="Price"
                className="w-full p-2 border rounded"
                value={editingProduct ? editingProduct.price : newProduct.price}
                onChange={(e) =>
                  editingProduct
                    ? setEditingProduct({...editingProduct, price: parseFloat(e.target.value)})
                    : setNewProduct({...newProduct, price: parseFloat(e.target.value)})
                }
              />
              <input
                type="number"
                placeholder="Discount Price"
                className="w-full p-2 border rounded"
                value={editingProduct ? editingProduct.discount_price : newProduct.discount_price}
                onChange={(e) =>
                  editingProduct
                    ? setEditingProduct({...editingProduct, discount_price: parseFloat(e.target.value)})
                    : setNewProduct({...newProduct, discount_price: parseFloat(e.target.value)})
                }
              />
              <input
                type="number"
                placeholder="Weight"
                className="w-full p-2 border rounded"
                value={editingProduct ? editingProduct.weight : newProduct.weight}
                onChange={(e) =>
                  editingProduct
                    ? setEditingProduct({...editingProduct, weight: parseFloat(e.target.value)})
                    : setNewProduct({...newProduct, weight: parseFloat(e.target.value)})
                }
              />
              <input
                type="number"
                placeholder="Preparation Time (min)"
                className="w-full p-2 border rounded"
                value={editingProduct ? editingProduct.preparation_time : newProduct.preparation_time}
                onChange={(e) =>
                  editingProduct
                    ? setEditingProduct({...editingProduct, preparation_time: parseInt(e.target.value)})
                    : setNewProduct({...newProduct, preparation_time: parseInt(e.target.value)})
                }
              />
              <textarea
                placeholder="Ingredients"
                className="w-full p-2 border rounded"
                value={editingProduct ? editingProduct.ingredients : newProduct.ingredients}
                onChange={(e) =>
                  editingProduct
                    ? setEditingProduct({...editingProduct, ingredients: e.target.value})
                    : setNewProduct({...newProduct, ingredients: e.target.value})
                }
              />
              <input
                type="text"
                placeholder="Image URL"
                className="w-full p-2 border rounded"
                value={editingProduct ? editingProduct.image_url : newProduct.image_url}
                onChange={(e) =>
                  editingProduct
                    ? setEditingProduct({...editingProduct, image_url: e.target.value})
                    : setNewProduct({...newProduct, image_url: e.target.value})
                }
              />
              <select
                className="w-full p-2 border rounded"
                value={editingProduct ? editingProduct.category_id : newProduct.category_id}
                onChange={(e) =>
                  editingProduct
                    ? setEditingProduct({...editingProduct, category_id: parseInt(e.target.value)})
                    : setNewProduct({...newProduct, category_id: parseInt(e.target.value)})
                }
              >
                <option value="">Select Category</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
              <div className="flex flex-wrap">
                <label className="flex items-center mr-4">
                  <input
                    type="checkbox"
                    className="mr-2"
                    checked={editingProduct ? editingProduct.is_active : newProduct.is_active}
                    onChange={(e) =>
                      editingProduct
                        ? setEditingProduct({...editingProduct, is_active: e.target.checked})
                        : setNewProduct({...newProduct, is_active: e.target.checked})
                    }
                  />
                  Active
                </label>
                <label className="flex items-center mr-4">
                  <input
                    type="checkbox"
                    className="mr-2"
                    checked={editingProduct ? editingProduct.is_stop_list : newProduct.is_stop_list}
                    onChange={(e) =>
                      editingProduct
                        ? setEditingProduct({...editingProduct, is_stop_list: e.target.checked})
                        : setNewProduct({...newProduct, is_stop_list: e.target.checked})
                    }
                  />
                  Stop List
                </label>
                <label className="flex items-center mr-4">
                  <input
                    type="checkbox"
                    className="mr-2"
                    checked={editingProduct ? editingProduct.is_recommended : newProduct.is_recommended}
                    onChange={(e) =>
                      editingProduct
                        ? setEditingProduct({...editingProduct, is_recommended: e.target.checked})
                        : setNewProduct({...newProduct, is_recommended: e.target.checked})
                    }
                  />
                  Recommended
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="mr-2"
                    checked={editingProduct ? editingProduct.is_new : newProduct.is_new}
                    onChange={(e) =>
                      editingProduct
                        ? setEditingProduct({...editingProduct, is_new: e.target.checked})
                        : setNewProduct({...newProduct, is_new: e.target.checked})
                    }
                  />
                  New
                </label>
              </div>
              <div className="flex space-x-2">
                {editingProduct ? (
                  <>
                    <button
                      className="flex-1 bg-green-500 text-white py-2 rounded hover:bg-green-600"
                      onClick={handleUpdateProduct}
                    >
                      Update
                    </button>
                    <button
                      className="flex-1 bg-gray-500 text-white py-2 rounded hover:bg-gray-600"
                      onClick={() => setEditingProduct(null)}
                    >
                      Cancel
                    </button>
                  </>
                ) : (
                  <button
                    className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
                    onClick={handleCreateProduct}
                  >
                    Add Product
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Products List */}
          {products.map((product) => {
            const category = categories.find(cat => cat.id === product.category_id);
            return (
              <div key={product.id} className="bg-white p-4 rounded-lg shadow">
                <h3 className="font-semibold text-lg">{product.name}</h3>
                <p className="text-gray-600 text-sm">{product.description}</p>
                <p className="text-blue-500 font-semibold">Price: {product.price}</p>
                <p className="text-gray-500 text-xs">Category: {category?.name || 'Uncategorized'}</p>
                <div className="mt-2 flex space-x-2">
                  <button
                    className="text-blue-500 hover:text-blue-700"
                    onClick={() => setEditingProduct(product)}
                  >
                    Edit
                  </button>
                  <button
                    className="text-red-500 hover:text-red-700"
                    onClick={() => handleDeleteProduct(product.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default MenuManagementPage;