// Esqueleto generado por spec2code. Módulo: Misiones y progresión
// NO es una solución: clases y firmas con TODO. Completa la lógica y audita contra la spec.
package rpgmanager.misionesyprogresion;

import java.time.LocalDate;

/** IntentoMision. Trazabilidad: RF-02, RF-03, RF-04, RF-05, RF-06, RF-07, RF-08, RF-09, RF-10. */
public class IntentoMision {
    private int idIntento;
    private int personaje;
    private int mision;
    private String estado;
    private int avance;
    private LocalDate fechaInicio;
    private LocalDate fechaCierre;

    public IntentoMision(int idIntento, int personaje, int mision, String estado, int avance, LocalDate fechaInicio, LocalDate fechaCierre) {
        this.idIntento = idIntento;
        this.personaje = personaje;
        this.mision = mision;
        this.estado = estado;
        this.avance = avance;
        this.fechaInicio = fechaInicio;
        this.fechaCierre = fechaCierre;
    }

    // TODO: getters y setters (encapsulamiento)

    /** completar (RF-04). */
    public void completar() {
        throw new UnsupportedOperationException("TODO: implementar IntentoMision.completar");
    }

    /** abandonar (RF-09). */
    public void abandonar() {
        throw new UnsupportedOperationException("TODO: implementar IntentoMision.abandonar");
    }

    /**
     * registrar_avance (RF-10).
     * @param unidades argumento de tipo int
     */
    public void registrarAvance(int unidades) {
        throw new UnsupportedOperationException("TODO: implementar IntentoMision.registrar_avance");
    }
}
