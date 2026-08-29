"""
Precision VRT Solo - Configuração de Segurança

Configurações de segurança e ambiente do sistema.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings

class SecuritySettings(BaseSettings):
    """Configurações de Segurança"""
    
    # JWT Settings
    JWT_SECRET_KEY: str = "precision_vrt_solo_secret_key_2024_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database Settings
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/precision_vrt_solo"
    DATABASE_TEST_URL: str = "postgresql://user:password@localhost:5432/precision_vrt_solo_test"
    
    # Application Settings
    APP_NAME: str = "Precision VRT Solo"
    APP_VERSION: str = "1.0.0"
    APP_DEBUG: bool = False
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    
    # Security Settings
    SECURITY_BCRYPT_ROUNDS: int = 12
    SECURITY_PASSWORD_COMPLEXITY: bool = True
    SECURITY_RATE_LIMIT_LOGIN: int = 5
    SECURITY_RATE_LIMIT_TOKEN: int = 10
    SECURITY_SESSION_TIMEOUT: int = 1800  # 30 minutes
    SECURITY_COOKIE_SECURE: bool = True
    SECURITY_COOKIE_HTTPONLY: bool = True
    SECURITY_COOKIE_SAMESITE: str = "lax"
    
    # Email Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "your-email@gmail.com"
    SMTP_PASSWORD: str = "your-app-password"
    SMTP_USE_TLS: bool = True
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "logs/app.log"
    
    # Upload Settings
    UPLOAD_MAX_SIZE: int = 10485760  # 10MB
    UPLOAD_ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf", "xlsx", "csv"]
    
    # Cache Settings
    CACHE_TYPE: str = "redis"
    CACHE_URL: str = "redis://localhost:6379/0"
    CACHE_DEFAULT_TIMEOUT: int = 300
    
    # API Security Settings
    API_RATE_LIMIT: int = 100
    API_RATE_LIMIT_PER_MINUTE: int = 10
    API_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    API_CORS_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    API_CORS_HEADERS: List[str] = ["*"]
    
    # Monitoring Settings
    MONITORING_ENABLED: bool = True
    MONITORING_ENDPOINT: str = "/health"
    MONITORING_METRICS: bool = True
    MONITORING_LOGS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_cors_origins_regex(self) -> str:
        """Expressão regular para origens CORS"""
        if not self.API_CORS_ORIGINS:
            return ""
        
        escaped_origins = [origin.replace(".", r"\.").replace("*", ".*") for origin in self.API_CORS_ORIGINS]
        return "|".join(escaped_origins)

# Instância global de configurações
security_settings = SecuritySettings()

# Roles e Permissões
class Roles:
    ADMIN = "admin"
    CONSULTOR = "consultor"
    FINANCEIRO = "financeiro"
    TECNICO = "tecnico"

class Permissions:
    # Dashboard Permissions
    DASHBOARD_READ = "dashboard:read"
    DASHBOARD_WRITE = "dashboard:write"
    
    # Users Permissions
    USERS_READ = "usuarios:read"
    USERS_WRITE = "usuarios:write"
    
    # Clients Permissions
    CLIENTS_READ = "clientes:read"
    CLIENTS_WRITE = "clientes:write"
    
    # Financial Permissions
    FINANCIAL_READ = "financeiro:read"
    FINANCIAL_WRITE = "financeiro:write"
    
    # Prescription Permissions
    PRESCRIPTION_READ = "prescricao:read"
    PRESCRIPTION_WRITE = "prescricao:write"
    
    # Configuration Permissions
    CONFIG_READ = "configuracoes:read"
    CONFIG_WRITE = "configuracoes:write"

# Role Mapping
ROLE_PERMISSIONS = {
    Roles.ADMIN: [
        Permissions.DASHBOARD_READ,
        Permissions.DASHBOARD_WRITE,
        Permissions.USERS_READ,
        Permissions.USERS_WRITE,
        Permissions.CLIENTS_READ,
        Permissions.CLIENTS_WRITE,
        Permissions.FINANCIAL_READ,
        Permissions.FINANCIAL_WRITE,
        Permissions.PRESCRIPTION_READ,
        Permissions.PRESCRIPTION_WRITE,
        Permissions.CONFIG_READ,
        Permissions.CONFIG_WRITE,
    ],
    Roles.CONSULTOR: [
        Permissions.DASHBOARD_READ,
        Permissions.CLIENTS_READ,
        Permissions.PRESCRIPTION_READ,
        Permissions.CONFIG_READ,
    ],
    Roles.FINANCEIRO: [
        Permissions.DASHBOARD_READ,
        Permissions.CLIENTS_READ,
        Permissions.FINANCIAL_READ,
        Permissions.FINANCIAL_WRITE,
    ],
    Roles.TECNICO: [
        Permissions.DASHBOARD_READ,
        Permissions.CLIENTS_READ,
        Permissions.CONFIG_READ,
    ],
}

# User Credentials for Testing
TEST_USERS = {
    "admin": {
        "password": "admin123",
        "role": Roles.ADMIN,
        "email": "admin@precisionvrt.com.br",
    },
    "consultor": {
        "password": "consultor123",
        "role": Roles.CONSULTOR,
        "email": "consultor@precisionvrt.com.br",
    },
    "financeiro": {
        "password": "financeiro123",
        "role": Roles.FINANCEIRO,
        "email": "financeiro@precisionvrt.com.br",
    },
    "tecnico": {
        "password": "tecnico123",
        "role": Roles.TECNICO,
        "email": "tecnico@precisionvrt.com.br",
    },
}

def get_user_permissions(role: str) -> List[str]:
    """Obter permissões para um papel"""
    return ROLE_PERMISSIONS.get(role, [])

def has_permission(user_permissions: List[str], required_permission: str) -> bool:
    """Verificar se usuário tem permissão"""
    # Admin tem todas as permissões
    if Permissions.USERS_READ in user_permissions:
        return True
    
    return required_permission in user_permissions

def get_user_info(username: str) -> Optional[dict]:
    """Obter informações do usuário de teste"""
    user_data = TEST_USERS.get(username.lower())
    if not user_data:
        return None
    
    return {
        "username": username,
        "email": user_data["email"],
        "role": user_data["role"],
        "permissions": get_user_permissions(user_data["role"]),
    }