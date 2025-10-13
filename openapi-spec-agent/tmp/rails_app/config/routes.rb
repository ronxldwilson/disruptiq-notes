# tmp/rails_app/config/routes.rb
Rails.application.routes.draw do
  get 'articles', to: 'articles#index'
  post 'articles', to: 'articles#create'
  get 'articles/:id', to: 'articles#show'
  put 'articles/:id', to: 'articles#update'
  delete 'articles/:id', to: 'articles#destroy'

  resources :users

  # Defines the root path route ("/")
  # root "posts#index"
end
