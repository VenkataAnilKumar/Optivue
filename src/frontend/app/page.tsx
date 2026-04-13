import { redirect } from 'next/navigation';

export default function HomePage() {
  // Redirect to analyst dashboard by default; auth guards control access
  redirect('/dashboard');
}
