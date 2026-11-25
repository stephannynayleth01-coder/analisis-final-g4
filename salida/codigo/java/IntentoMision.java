// Esqueleto generado por spec2code. Módulo: Misiones y progresión
// NO es una solución: clases y firmas con TODO. Completa la lógica y audita contra la spec.
package rpgmanager.misionesyprogresion;

import java.time.LocalDate;

/** IntentoMision. Trazabilidad: RN-01, RN-02, RN-03, RN-04, RN-05, RN-06, RN-07, RN-08. */
public class IntentoMision {
    private int identificador;
    private int personaje;
    private int mision;
    private String estado;
    private int avance;
    private LocalDate fechaInicio;
    private LocalDate fechaCierre;
    private Mision mision; // asociacion: pertenece_a ()

    public IntentoMision(int identificador, int personaje, int mision, String estado, int avance, LocalDate fechaInicio, LocalDate fechaCierre) {
        this.identificador = identificador;
        this.personaje = personaje;
        this.mision = mision;
        this.estado = estado;
        this.avance = avance;
        this.fechaInicio = fechaInicio;
        this.fechaCierre = fechaCierre;
    }

    // TODO: getters y setters (encapsulamiento)

    /** registrar_avance (RF-10). */
    public void registrarAvance() {
        throw new UnsupportedOperationException("TODO: implementar IntentoMision.registrar_avance");
    }

    /** completar (RF-04). */
    public void completar() {
        throw new UnsupportedOperationException("TODO: implementar IntentoMision.completar");
    }

    /** abandonar (RF-09). */
    public void abandonar() {
        throw new UnsupportedOperationException("TODO: implementar IntentoMision.abandonar");
    }
}
