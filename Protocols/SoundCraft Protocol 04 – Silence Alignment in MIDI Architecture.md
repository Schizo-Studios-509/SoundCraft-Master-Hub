# SoundCraft Protocol 04 – Silence Alignment in MIDI Architecture

**Purpose:**  
To ensure uniform synchronization of MIDI stems across all DAWs.

—

## 1. Alignment Rule
Every MIDI stem must:
- Begin at absolute time 0:00.  
- Include structured silence equal to its pre-entry rest.  
This guarantees that all stems line up when imported simultaneously.

—

## 2. Implementation Guidelines
| Item | Standard |
|——|————|
| **Tempo Map** | Same for all stems (see master metadata) |
| **Time Signature** | Global project setting |
| **Pre-Roll Silence** | Must extend to 0:00 for visual alignment |

—

**Protocol Version:** 1.0 (2025)