import React from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from './AuthContext';
import { LogOut, User as UserIcon } from 'lucide-react';

export const LoginButton: React.FC = () => {
  const { login, logout, user, isAuthenticated } = useAuth();

  if (isAuthenticated && user) {
    return (
      <div className="flex items-center gap-4 bg-white/10 p-2 rounded-lg border border-white/20">
        <div className="flex items-center gap-2">
          {user.picture ? (
            <img src={user.picture} alt={user.name} className="w-8 h-8 rounded-full border border-white/20" />
          ) : (
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center border border-white/20">
              <UserIcon className="w-4 h-4 text-white" />
            </div>
          )}
          <div className="flex flex-col">
            <span className="text-sm font-medium text-white leading-none">{user.name}</span>
            <span className="text-xs text-white/60 leading-tight truncate max-w-[120px]">{user.email}</span>
          </div>
        </div>
        <button
          onClick={logout}
          className="p-2 hover:bg-white/10 rounded-full transition-colors group"
          title="Odśwież / Wyloguj"
        >
          <LogOut className="w-4 h-4 text-white/70 group-hover:text-white" />
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center">
      <GoogleLogin
        onSuccess={(credentialResponse) => {
          if (credentialResponse.credential) {
            login(credentialResponse.credential);
          }
        }}
        onError={() => {
          console.error('Login Failed');
        }}
        useOneTap
        theme="filled_blue"
        shape="pill"
      />
    </div>
  );
};
