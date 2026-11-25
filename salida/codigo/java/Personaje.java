// Esqueleto generado por spec2code. Módulo: Misiones y progresión
// NO es una solución: clases y firmas con TODO. Completa la lógica y audita contra la spec.
package rpgmanager.misionesyprogresion;

import java.util.ArrayList;
import java.util.List;

/** Personaje. Trazabilidad: RN-01, RN-02, RN-03, RN-04, RN-05, RN-06, RN-07, RN-08. */
public class Personaje {
    private int identificador;
    private String nombre;
    private int nivel;
    private int experienciaDisponible;
    private List<IntentoMision> intentoMisions = new ArrayList<>(); // asociacion: tiene ()

    public Personaje(int identificador, String nombre, int nivel, int experienciaDisponible) {
        this.identificador = identificador;
        this.nombre = nombre;
        this.nivel = nivel;
        this.experienciaDisponible = experienciaDisponible;
    }

    // TODO: getters y setters (encapsulamiento)

    /** consultar_misiones_disponibles (RF-01). */
    public void consultarMisionesDisponibles() {
        throw new UnsupportedOperationException("TODO: implementar Personaje.consultar_misiones_disponibles");
    }

    /** aceptar_mision (RF-02). */
    public void aceptarMision() {
        throw new UnsupportedOperationException("TODO: implementar Personaje.aceptar_mision");
    }

    /** consultar_avance (RF-03). */
    public void consultarAvance() {
        throw new UnsupportedOperationException("TODO: implementar Personaje.consultar_avance");
    }

    /** completar_mision (RF-04). */
    public void completarMision() {
        throw new UnsupportedOperationException("TODO: implementar Personaje.completar_mision");
    }

    /** consultar_progresion (RF-06). */
    public void consultarProgresion() {
        throw new UnsupportedOperationException("TODO: implementar Personaje.consultar_progresion");
    }

    /** consultar_historial (RF-08). */
    public void consultarHistorial() {
        throw new UnsupportedOperationException("TODO: implementar Personaje.consultar_historial");
    }

    /** abandonar_mision (RF-09). */
    public void abandonarMision() {
        throw new UnsupportedOperationException("TODO: implementar Personaje.abandonar_mision");
    }
}
