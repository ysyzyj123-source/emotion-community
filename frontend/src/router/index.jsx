import { createBrowserRouter } from 'react-router-dom'
import App from '../App'
import Login from '../pages/Login'
import Register from '../pages/Register'
import PostList from '../pages/PostList'
import PostDetail from '../pages/PostDetail'
import CreatePost from '../pages/CreatePost'
import RequireAuth from '../components/RequireAuth'

const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/register',
    element: <Register />,
  },
  {
    path: '/',
    element: (
      <RequireAuth>
        <App />
      </RequireAuth>
    ),
    children: [
      { index: true, element: <PostList /> },
      { path: 'post/:id', element: <PostDetail /> },
      { path: 'post/new', element: <CreatePost /> },
    ],
  },
])

export default router
