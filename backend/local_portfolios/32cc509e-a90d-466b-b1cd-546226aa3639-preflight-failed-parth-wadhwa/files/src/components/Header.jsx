import React from 'react';
import { AiOutlineGithub, AiOutlineLinkedin } from 'react-icons/ai';

export default function Header() {
 return (
 <header className="header bg-gray-900 text-white p-4 flex justify-center items-center flex-col">
 <h1 className="text-5xl font-bold mb-4">Parth Wadhwa</h1>
 <p className="text-xl mb-8">AI Full-Stack Developer</p>
 <ul className="flex justify-center items-center space-x-4">
 <li>
 <a href="https://github.com/ParthWadhwa14" target="_blank" rel="noreferrer" className="hover:text-gray-300">
 <AiOutlineGithub size={24} />
 </a>
 </li>
 <li>
 <a href="https://www.linkedin.com/in/parth-wadhwa-855650323/" target="_blank" rel="noreferrer" className="hover:text-gray-300">
 <AiOutlineLinkedin size={24} />
 </a>
 </li>
 </ul>
 </header>
 );
}