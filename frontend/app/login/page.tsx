"use client";

import TextInput from "@/components/common/form-inputs/TextInput";
import "@/styles/common/form.scss";

export default function LoginPage() {
  function func() {}
  return (
    <TextInput
      name="email"
      type="email"
      label="Email"
      value=""
      onChange={func}
      autoComplete=""
    />
  );
}
