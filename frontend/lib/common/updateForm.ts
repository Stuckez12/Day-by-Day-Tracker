export function updateForm<T extends Record<string, unknown>>(
  e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  form: T,
  setForm: React.Dispatch<React.SetStateAction<T>>,
) {
  const { name, value } = e.target;
  setForm({
    ...form,
    [name]: value,
  });
}
