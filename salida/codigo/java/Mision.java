// Esqueleto generado por spec2code. Módulo: Misiones y progresión
// NO es una solución: clases y firmas con TODO. Completa la lógica y audita contra la spec.
package rpgmanager.misionesyprogresion;

/** Mision. Trazabilidad: RF-01, RF-02, RF-03, RF-04, RF-05, RF-07, RF-08, RF-09. */
public class Mision {
    private int idMision;
    private String nombre;
    private int nivelRequerido;
    private int objetivoTotal;
    private int recompensaExperiencia;

    public Mision(int idMision, String nombre, int nivelRequerido, int objetivoTotal, int recompensaExperiencia) {
        this.idMision = idMision;
        this.nombre = nombre;
        this.nivelRequerido = nivelRequerido;
        this.objetivoTotal = objetivoTotal;
        this.recompensaExperiencia = recompensaExperiencia;
    }

    // TODO: getters y setters (encapsulamiento)

    /** consultar_misiones_disponibles (RF-01). */
    public void consultarMisionesDisponibles() {
        throw new UnsupportedOperationException("TODO: implementar Mision.consultar_misiones_disponibles");
    }
}
