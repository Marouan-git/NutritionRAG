// NavBar.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import logo from '../logo_removedbg.png'

const Navbar = () => {
  return (
    <nav className="flex items-center justify-between p-4 bg-green-100 text-white">
      <Link to="/" className="flex items-center">
        <img
          src={logo}
          alt="Logo"
          style={{ width: 70, height: 70 }}
        />
        <span className="ml-3 font-bold text-xl text-green-800">NutrIA</span>
      </Link>
      <div className="flex space-x-7">
        <Link to="/profile" className="ml-2 font-bold hover:underline text-green-800">
          Profile
        </Link>
        <Link to="/chat" className="ml-2 font-bold hover:underline text-green-800">
          Chat
        </Link>
        <Link to="/upload" className="ml-2 font-bold hover:underline text-green-800">
          Upload
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;

// import React from 'react';
// import { Link } from 'react-router-dom';
// import logo from '../logo_removedbg.png'

// const Navbar = () => {
//   return (
//     <nav className="flex items-center justify-between p-4 bg-green-100 text-white">
//       <div className="flex items-center">
//         <img

//           src={logo}
//           alt="Logo"
//           // resize the logo
//           style={{ width: 70, height: 70 }}
//         />
//         <span className="ml-3 font-bold text-xl text-green-800">NutrIA</span>
//       </div>
//       <div className="flex space-x-7">
//         <Link to="/profile" className="ml-2 font-bold hover:underline text-green-800">
//           Profile
//         </Link>
//         <Link to="/chat" className="ml-2 font-bold hover:underline text-green-800">
//           Chat
//         </Link>
//       </div>
//     </nav>
//   );
// };

// export default Navbar;

