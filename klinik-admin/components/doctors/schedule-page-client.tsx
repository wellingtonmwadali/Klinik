"use client";

import { useState, useEffect } from "react";
import { DoctorScheduleForm } from "@/components/doctors/schedule-form";

type Doctor = {
  id: number;
  full_name: string;
  specialization: string;
  email: string;
  is_active: boolean;
};

type User = {
  id: number;
  username: string;
  email: string;
  role?: string | null;
  is_staff: boolean;
  doctor_profile?: {
    id: number | string;
  };
};

type SchedulePageClientProps = {
  doctors: Doctor[];
  currentUser: User | null;
  error: string | null;
};

export function SchedulePageClient({
  doctors,
  currentUser,
  error: initialError,
}: SchedulePageClientProps) {
  const [selectedDoctorId, setSelectedDoctorId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(initialError);

  const isDoctor = !!currentUser?.doctor_profile;
  const isAdmin = currentUser?.role === "ADMIN" && !isDoctor;

  const validDoctors = doctors.filter(
    (doctor) => typeof doctor.id === "number" && !Number.isNaN(doctor.id)
  );
  const selectedDoctor = selectedDoctorId
    ? validDoctors.find((doctor) => doctor.id === selectedDoctorId) ?? null
    : null;

  useEffect(() => {
    console.log("=== Schedule Page Debug ===");
    console.log("Current User:", currentUser);
    console.log("Role:", currentUser?.role);
    console.log("Is Admin:", isAdmin);
    console.log("Is Doctor:", isDoctor);
    console.log("Doctor Profile ID:", currentUser?.doctor_profile?.id);
    console.log("Doctors List:", doctors);

    if (!isAdmin && isDoctor && currentUser?.doctor_profile?.id != null) {
      const doctorProfileId = Number(currentUser.doctor_profile.id);
      if (!Number.isNaN(doctorProfileId)) {
        const currentDoctor = validDoctors.find((d) => d.id === doctorProfileId);
        if (currentDoctor) {
          setSelectedDoctorId(currentDoctor.id);
        }
      }
    }
  }, [doctors, currentUser, isAdmin, isDoctor]);

  const canEditDoctor = (doctor: Doctor | null) => {
    if (!doctor || !currentUser) return false;
    if (isAdmin) return true; // Admin can edit anyone
    if (currentUser.doctor_profile?.id === doctor.id) return true; // Doctor can edit own
    return false;
  };

  return (
    <div className="mt-6 space-y-6">
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-900 dark:bg-red-950">
          <p className="text-sm text-red-700 dark:text-red-200">{error}</p>
        </div>
      )}

      {/* Doctor Selection - Only show for admins */}
      {isAdmin ? (
        <div className="rounded-lg border border-zinc-200 p-6 dark:border-zinc-800">
          <label
            htmlFor="doctor-select"
            className="block text-sm font-medium text-zinc-950 dark:text-zinc-50"
          >
            Select Doctor
          </label>
          <select
            id="doctor-select"
            value={selectedDoctor?.id ?? ""}
            onChange={(e) => {
              const doctorId = Number(e.target.value);
              setSelectedDoctorId(Number.isNaN(doctorId) ? null : doctorId);
            }}
            className="mt-2 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm text-zinc-950 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-50"
          >
            <option value="">Choose a doctor...</option>
            {doctors.map((doctor) => (
              <option key={doctor.id} value={doctor.id}>
                Dr. {doctor.full_name} ({doctor.specialization})
              </option>
            ))}
          </select>
        </div>
      ) : (
        // For doctors, show their selected doctor info (not editable)
        selectedDoctor && (
          <div className="rounded-lg border border-zinc-200 bg-zinc-50 p-6 dark:border-zinc-800 dark:bg-zinc-900">
            <p className="text-sm text-zinc-600 dark:text-zinc-400">Managing schedule for:</p>
            <p className="mt-2 text-lg font-medium text-zinc-950 dark:text-zinc-50">
              Dr. {selectedDoctor.full_name}
            </p>
            <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
              {selectedDoctor.specialization}
            </p>
          </div>
        )
      )}

      {/* Schedule Form */}
      {selectedDoctor ? (
        canEditDoctor(selectedDoctor) ? (
          <DoctorScheduleForm doctor={selectedDoctor} />
        ) : (
          <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 dark:border-yellow-900 dark:bg-yellow-950">
            <p className="text-sm text-yellow-700 dark:text-yellow-200">
              You don't have permission to edit this doctor's schedule.
            </p>
          </div>
        )
      ) : (
        <div className="rounded-lg border border-zinc-200 p-8 text-center dark:border-zinc-800">
          <p className="text-zinc-500 dark:text-zinc-400">
            {isAdmin
              ? "Select a doctor to manage their schedule"
              : "Loading your schedule..."}
          </p>
        </div>
      )}
    </div>
  );
}