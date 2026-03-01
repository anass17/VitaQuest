import React, { useEffect } from "react";
import { useNavigate } from "react-router";


const Logout: React.FC = () => {
  const navigate = useNavigate();

    useEffect(() => {
        if (localStorage.getItem("access_token")) {
            localStorage.clear()
        }

        navigate('/login')
    }, [])

  return (
    <></>
  );
};

export default Logout;