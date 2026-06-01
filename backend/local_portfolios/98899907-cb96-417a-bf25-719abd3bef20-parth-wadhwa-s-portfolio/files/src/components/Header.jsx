import React from 'react';
import { AiOutlineGithub, AiOutlineLinkedin } from 'lucide-react';

const Header = () => {
 return (
 <header className="header bg-gray-900 text-white p-4 flex justify-center items-center">
 <h1 className="text-5xl font-bold">Parth Wadhwa</h1>
 <p className="text-xl">B.Tech Chemical Engineering</p>
 <ul className="social-links flex justify-center items-center">
 <li>
 <a href="https://www.linkedin.com/in/parth-wadhwa-855650323" target="_blank" rel="noopener noreferrer" className="text-white hover:text-gray-300">
 <AiOutlineLinkedin size={24} />
 </a>
 </li>
 <li>
 <a href="https://github.com/parthwadhwa" target="_blank" rel="noopener noreferrer" className="text-white hover:text-gray-300">
 <AiOutlineGithub size={24} />
 </a>
 </li>
 </ul>
 </header>
 );
};

export default Header;
