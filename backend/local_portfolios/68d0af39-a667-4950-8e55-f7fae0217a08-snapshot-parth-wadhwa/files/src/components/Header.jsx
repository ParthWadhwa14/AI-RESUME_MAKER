import React from 'react';
import { FiGithub, FiLinkedin } from 'lucide-react';

export default function Header() {
 return (
 <header className="header flex justify-center py-4">
 <h1 className="text-3xl font-bold">Parth Wadhwa</h1>
 <p className="text-xl">AI Full-Stack Developer</p>
 <ul className="flex justify-center mt-4">
 <li className="mr-4">
 <a href="https://github.com/ParthWadhwa14" target="_blank" rel="noreferrer">
 <FiGithub size={24} />
 </a>
 </li>
 <li>
 <a href="https://www.linkedin.com/in/parth-wadhwa-855650323/" target="_blank" rel="noreferrer">
 <FiLinkedin size={24} />
 </a>
 </li>
 </ul>
 </header>
 );
}
