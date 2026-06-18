export function updateForm<T extends Record<string, any>>(
  e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  form: T,
  setForm: Function,
) {
  const { name, value } = e.target;
  setForm({
    ...form,
    [name]: value,
  });
}
