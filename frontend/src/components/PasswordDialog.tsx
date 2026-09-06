import { useState, type FormEvent } from 'react'

import { errorMessage, useSetPasswordMutation } from '@/services/authApi'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Field, FieldDescription, FieldGroup, FieldLabel } from '@/components/ui/field'
import { Input } from '@/components/ui/input'

interface PasswordDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  hasPassword: boolean
}

export function PasswordDialog({ open, onOpenChange, hasPassword }: PasswordDialogProps) {
  const [setPassword, { isLoading }] = useSetPasswordMutation()
  const [password, setPasswordValue] = useState('')
  const [error, setError] = useState<string | null>(null)

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    try {
      await setPassword({ password }).unwrap()
      setPasswordValue('')
      onOpenChange(false)
    } catch (err) {
      setError(errorMessage(err))
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{hasPassword ? 'Change password' : 'Add a password'}</DialogTitle>
          <DialogDescription>
            {hasPassword
              ? 'Set a new password to log in with email.'
              : 'You signed up with Google. Set a password to also log in with your email.'}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={onSubmit}>
          {error && (
            <p
              role="alert"
              className="mb-4 rounded-md border border-destructive/20 bg-destructive/10 px-3 py-2 text-sm text-destructive"
            >
              {error}
            </p>
          )}
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="new-password">
                {hasPassword ? 'New password' : 'Password'}
              </FieldLabel>
              <Input
                id="new-password"
                type="password"
                required
                minLength={8}
                autoComplete="new-password"
                placeholder="At least 8 characters"
                value={password}
                onChange={(e) => setPasswordValue(e.target.value)}
              />
              <FieldDescription>Minimum 8 characters.</FieldDescription>
            </Field>
          </FieldGroup>
          <DialogFooter className="mt-4">
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Saving…' : hasPassword ? 'Change password' : 'Add password'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}