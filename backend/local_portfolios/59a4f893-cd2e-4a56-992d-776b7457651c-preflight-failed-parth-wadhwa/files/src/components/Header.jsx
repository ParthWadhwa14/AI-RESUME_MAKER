import React from 'react';
import { AiOutlineGithub, AiOutlineLinkedin } from 'lucide-react';

function Header() {
 return (
 <header className="header">
 <h1>Parth Wadhwa</h1>
 <p>B.Tech Chemical Engineering</p>
 <ul className="social-links">
 <li><a href="https://www.linkedin.com/in/parth-wadhwa-855650323" target="_blank" rel="noreferrer"><AiOutlineLinkedin size={24} /></a></li>
 </ul>
 </header>
 );
}

export default Header;