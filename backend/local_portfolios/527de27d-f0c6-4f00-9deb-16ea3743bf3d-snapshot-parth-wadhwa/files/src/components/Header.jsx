import React from 'react';
import { Linkedin } from 'lucide-react';

export default function Header() {
 return (
 <header className="header bg-gray-900 text-white p-4 flex justify-center">
 <h1 className="text-5xl">Parth Wadhwa</h1>
 <p className="text-lg">B.Tech Chemical Engineering</p>
 <ul className="social-links flex justify-center">
 <li>
 <a href="https://www.linkedin.com/in/parth-wadhwa-855650323" target="_blank" rel="noreferrer" className="hover:text-blue-500">
 <Linkedin size={24} />
 </a>
 </li>
 </ul>
 </header>
 );
}