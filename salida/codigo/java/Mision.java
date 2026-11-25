// Esqueleto generado por spec2code. Módulo: Misiones y progresión
// NO es una solución: clases y firmas con TODO. Completa la lógica y audita contra la spec.
package rpgmanager.misionesyprogresion;

/** Mision. Trazabilidad: RN-01, RN-02, RN-03, RN-04, RN-05, RN-06, RN-07, RN-08. */
public class Mision {
    private int identificador;
    private String nombre;
    private int nivelRequerido;
    private int objetivoTotal;
    private int recompensaExperiencia;

    public Mision(int identificador, String nombre, int nivelRequerido, int objetivoTotal, int recompensaExperiencia) {
        this.identificador = identificador;
        this.nombre = nombre;
        this.nivelRequerido = nivelRequerido;
        this.objetivoTotal = objetivoTotal;
        this.recompensaExperiencia = recompensaExperiencia;
    }

    // TODO: getters y setters (encapsulamiento)

    /** consultar_disponibilidad (RF-01). */
    public void consultarDisponibilidad() {
        throw new UnsupportedOperationException("TODO: implementar Mision.consultar_disponibilidad");
    }
}
