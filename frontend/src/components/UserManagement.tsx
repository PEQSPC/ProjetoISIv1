import { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, TextField, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, IconButton, Alert, CircularProgress,
  FormControl, InputLabel, Select, MenuItem, Box, Typography, Chip
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import api from '../api/axios';
import { type User } from '../types';

interface UserManagementProps {
  open: boolean;
  onClose: () => void;
  currentUserId: number;
}

export default function UserManagement({ open, onClose, currentUserId }: UserManagementProps) {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form state
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newUsername, setNewUsername] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newRole, setNewRole] = useState<'admin' | 'user'>('user');
  const [creating, setCreating] = useState(false);

  const fetchUsers = async () => {
    try {
      setError(null);
      const res = await api.get('/auth/users');
      setUsers(res.data);
    } catch (err) {
      console.error('Erro ao carregar utilizadores:', err);
      setError('Erro ao carregar utilizadores');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open) {
      setLoading(true);
      fetchUsers();
    }
  }, [open]);

  const handleCreate = async () => {
    if (!newUsername.trim() || !newPassword.trim()) {
      setError('Username e password são obrigatórios');
      return;
    }

    setCreating(true);
    setError(null);

    try {
      await api.post('/auth/users', {
        username: newUsername,
        password: newPassword,
        role: newRole
      });
      setSuccess(`Utilizador "${newUsername}" criado com sucesso`);
      setNewUsername('');
      setNewPassword('');
      setNewRole('user');
      setShowCreateForm(false);
      fetchUsers();
    } catch (err: unknown) {
      let errorMessage = 'Erro ao criar utilizador';
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosError = err as { response?: { data?: { detail?: string } } };
        errorMessage = axiosError.response?.data?.detail || errorMessage;
      }
      setError(errorMessage);
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (userId: number, username: string) => {
    if (!confirm(`Tens a certeza que queres eliminar o utilizador "${username}"?`)) {
      return;
    }

    try {
      await api.delete(`/auth/users/${userId}`);
      setSuccess(`Utilizador "${username}" eliminado com sucesso`);
      fetchUsers();
    } catch (err: unknown) {
      let errorMessage = 'Erro ao eliminar utilizador';
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosError = err as { response?: { data?: { detail?: string } } };
        errorMessage = axiosError.response?.data?.detail || errorMessage;
      }
      setError(errorMessage);
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '-';
    try {
      return new Date(dateString).toLocaleString('pt-PT');
    } catch {
      return dateString;
    }
  };

  const handleClose = () => {
    setShowCreateForm(false);
    setNewUsername('');
    setNewPassword('');
    setNewRole('user');
    setError(null);
    setSuccess(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Gestão de Utilizadores</Typography>
          <Button
            startIcon={<PersonAddIcon />}
            variant="contained"
            size="small"
            onClick={() => setShowCreateForm(!showCreateForm)}
          >
            {showCreateForm ? 'Cancelar' : 'Novo Utilizador'}
          </Button>
        </Box>
      </DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        {success && (
          <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        {showCreateForm && (
          <Paper sx={{ p: 2, mb: 2, backgroundColor: '#f5f5f5' }}>
            <Typography variant="subtitle1" gutterBottom>
              Criar Novo Utilizador
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'flex-end' }}>
              <TextField
                label="Username"
                value={newUsername}
                onChange={(e) => setNewUsername(e.target.value)}
                size="small"
                sx={{ minWidth: 150 }}
              />
              <TextField
                label="Password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                size="small"
                sx={{ minWidth: 150 }}
              />
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Role</InputLabel>
                <Select
                  value={newRole}
                  label="Role"
                  onChange={(e) => setNewRole(e.target.value as 'admin' | 'user')}
                >
                  <MenuItem value="user">User</MenuItem>
                  <MenuItem value="admin">Admin</MenuItem>
                </Select>
              </FormControl>
              <Button
                variant="contained"
                onClick={handleCreate}
                disabled={creating}
                sx={{ height: 40 }}
              >
                {creating ? <CircularProgress size={20} /> : 'Criar'}
              </Button>
            </Box>
          </Paper>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Username</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Estado</TableCell>
                  <TableCell>Criado em</TableCell>
                  <TableCell align="right">Ações</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.id}</TableCell>
                    <TableCell>
                      {user.username}
                      {user.id === currentUserId && (
                        <Chip label="Tu" size="small" color="primary" sx={{ ml: 1 }} />
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={user.role}
                        size="small"
                        color={user.role === 'admin' ? 'warning' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={user.is_active ? 'Ativo' : 'Inativo'}
                        size="small"
                        color={user.is_active ? 'success' : 'error'}
                      />
                    </TableCell>
                    <TableCell>{formatDate(user.created_at)}</TableCell>
                    <TableCell align="right">
                      <IconButton
                        color="error"
                        size="small"
                        onClick={() => handleDelete(user.id, user.username)}
                        disabled={user.id === currentUserId}
                        title={user.id === currentUserId ? 'Não podes eliminar-te a ti próprio' : 'Eliminar utilizador'}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Fechar</Button>
      </DialogActions>
    </Dialog>
  );
}
